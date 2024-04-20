import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import { Construct } from 'constructs';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as secretsmanager from 'aws-cdk-lib/aws-secretsmanager';

export class PreferenceLambdaStack extends cdk.Stack {
    public readonly lambda: lambda.Function;

    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);
    
        const layer = new lambda.LayerVersion(this, 'PoetryDependenciesLayer', {
            code: lambda.Code.fromAsset('../preference_lambda/layer.zip'),
            compatibleRuntimes: [lambda.Runtime.PYTHON_3_11],
            license: 'Apache-2.0',
            description: 'A layer to hold the poetry dependencies',
        });

        const dynamoDbTableArn = cdk.Fn.importValue('DynamoDbTableArn');
        const openSearchDomainArn = cdk.Fn.importValue('OpenSearchDomainArn');
        const openAiApiKeySecretArn = cdk.Fn.importValue('OpenAiApiKeySecretArn');

        const openAiApiKey = secretsmanager.Secret.fromSecretCompleteArn(this, 'OpenAiApiKey', openAiApiKeySecretArn).secretValue.toString();

        this.lambda = new lambda.Function(this, 'PreferenceLambda', {
            runtime: lambda.Runtime.PYTHON_3_11,
            code: lambda.Code.fromAsset('../preference_lambda'),
            handler: 'lambda_function.lambda_handler',
            memorySize: 128,
            timeout: cdk.Duration.minutes(15),
            environment: {
                DYNAMODB_TABLE_NAME: dynamoDbTableArn.split('/')[1],
                OPENAI_API_KEY: openAiApiKey,
                AWS_REGION: cdk.Stack.of(this).region,
            },
        });

        this.lambda.addLayers(layer);

        this.lambda.addToRolePolicy(new iam.PolicyStatement({
            actions: [
                'dynamodb:GetItem',
                'dynamodb:PutItem',
            ],
            resources: [dynamoDbTableArn],
        }));

        this.lambda.addToRolePolicy(new iam.PolicyStatement({
            actions: [
                'es:ESHttpGet',
                'es:ESHttpSearch',
                'es:ESHttp*',
            ],
            resources: [`${openSearchDomainArn}/*`],
        }));

        this.lambda.addToRolePolicy(new iam.PolicyStatement({
            actions: [
                'secretsmanager:GetSecretValue',
            ],
            resources: [openAiApiKeySecretArn],
        }));

        const api = new apigateway.RestApi(this, 'PreferenceApi', {
            restApiName: 'Preference Service',
            description: 'This service serves preferences.',
        });

        const preferenceLambdaIntegration = new apigateway.LambdaIntegration(this.lambda, {
            requestTemplates: { "application/json": '{ "statusCode": "200" }' }
        });

        api.root.addMethod('POST', preferenceLambdaIntegration);
    }
}