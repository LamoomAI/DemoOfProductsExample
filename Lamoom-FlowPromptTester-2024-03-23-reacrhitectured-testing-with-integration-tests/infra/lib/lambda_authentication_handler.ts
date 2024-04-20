import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as ssm from 'aws-cdk-lib/aws-ssm';
import { Construct } from 'constructs';

export class AuthenticationHandlerStack extends cdk.Stack {
    public readonly lambda: lambda.Function;

    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);

        const layer = new lambda.LayerVersion(this, 'PoetryDependenciesLayer', {
            code: lambda.Code.fromAsset('../backend/layer.zip'),
            compatibleRuntimes: [lambda.Runtime.PYTHON_3_11],
            license: 'Apache-2.0',
            description: 'A layer to hold the poetry dependencies',
        });

        const lambdaRole = new iam.Role(this, 'AuthenticationLambdaRole', {
            assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
            inlinePolicies: {
                CognitoPolicy: new iam.PolicyDocument({
                    statements: [
                        new iam.PolicyStatement({
                            actions: [
                                'cognito-idp:AdminInitiateAuth',
                                'cognito-idp:AdminRespondToAuthChallenge',
                            ],
                            resources: [
                                `arn:aws:cognito-idp:${this.region}:${this.account}:userpool/${ssm.StringParameter.valueForStringParameter(this, '/myapp/cognito_user_pool_id')}`,
                            ],
                        }),
                    ],
                }),
            },
        });

        lambdaRole.addToPolicy(new iam.PolicyStatement({
            actions: ['secretsmanager:GetSecretValue'],
            resources: [
                cdk.Stack.of(this).formatArn({
                    service: 'secretsmanager',
                    resource: 'secret',
                    resourceName: 'JWTSecretKey-*'
                })
            ],
        }));

        const environmentVariables = {
            IS_QA_ENV: ssm.StringParameter.valueForStringParameter(this, '/myapp/is_qa_env'),
            COGNITO_USER_POOL_ID: ssm.StringParameter.valueForStringParameter(this, '/myapp/cognito_user_pool_id'),
            COGNITO_CLIENT_ID: ssm.StringParameter.valueForStringParameter(this, '/myapp/cognito_client_id'),
        };

        this.lambda = new lambda.Function(this, 'AuthenticationHandler', {
            runtime: lambda.Runtime.PYTHON_3_11,
            code: lambda.Code.fromAsset('../backend'),
            handler: 'src.lambda_authentication_handler.lambda_handler',
            memorySize: 256,
            timeout: cdk.Duration.seconds(10),
            environment: environmentVariables,
            role: lambdaRole,
        });
        this.lambda.addLayers(layer);

        const mainInfraStackArn = cdk.Fn.importValue('MainInfraStackArn');
        this.lambda.addPermission('AllowMainInfraStackInvocation', {
            principal: new cdk.aws_iam.ServicePrincipal('cloudformation.amazonaws.com'),
            sourceArn: mainInfraStackArn,
        });

        new cdk.CfnOutput(this, 'AuthenticationHandlerLambdaArn', {
            value: this.lambda.functionArn,
            exportName: 'AuthenticationHandlerLambdaArn',
        });
    }
}