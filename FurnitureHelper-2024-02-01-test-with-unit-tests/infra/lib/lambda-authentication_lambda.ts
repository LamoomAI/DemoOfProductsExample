import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as secretsmanager from 'aws-cdk-lib/aws-secretsmanager';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Construct } from 'constructs';

export class AuthenticationLambdaStack extends cdk.Stack {
    public readonly lambda: lambda.Function;

    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);
        
        const layer = new lambda.LayerVersion(this, 'PoetryDependenciesLayer', {
            code: lambda.Code.fromAsset('../authentication_lambda/layer.zip'),
            compatibleRuntimes: [lambda.Runtime.PYTHON_3_11],
            license: 'Apache-2.0',
            description: 'A layer to hold the poetry dependencies',
        });

        // Fetch the Cognito User Pool ID and Client ID from Secrets Manager
        const cognitoUserPoolIdSecret = secretsmanager.Secret.fromSecretNameV2(this, 'CognitoUserPoolIdSecret', 'CognitoUserPoolId');
        const cognitoClientIdSecret = secretsmanager.Secret.fromSecretNameV2(this, 'CognitoClientIdSecret', 'CognitoClientId');

        // Pass the secrets to the Lambda function as environment variables
        this.lambda = new lambda.Function(this, 'AuthenticationLambda', {
            runtime: lambda.Runtime.PYTHON_3_11,
            code: lambda.Code.fromAsset('../authentication_lambda'),
            handler: 'lambda_function.lambda_handler',
            memorySize: 256,
            timeout: cdk.Duration.seconds(30),
            environment: {
                COGNITO_USER_POOL_ID: cognitoUserPoolIdSecret.secretValue.toString(),
                COGNITO_CLIENT_ID: cognitoClientIdSecret.secretValue.toString(),
            },
        });

        const userPool = secretsmanager.Secret.fromSecretNameV2(this, 'CognitoUserPoolIdSecret', 'CognitoUserPoolId');

        // Ensure the Lambda function has the minimum necessary permissions
        const policy = new iam.PolicyStatement({
            actions: ['cognito-idp:AdminInitiateAuth', 'cognito-idp:AdminRespondToAuthChallenge'],
            resources: [userPool.secretArn],
        });
        this.lambda.addToRolePolicy(policy);

        this.lambda.addLayers(layer);
    }
}