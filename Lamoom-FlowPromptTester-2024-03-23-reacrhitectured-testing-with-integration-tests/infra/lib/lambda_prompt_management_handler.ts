import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Construct } from 'constructs';

export class PromptManagementHandlerStack extends cdk.Stack {
    public readonly lambda: lambda.Function;

    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);

        // IAM role for the Lambda function
        const lambdaRole = new iam.Role(this, 'PromptManagementLambdaRole', {
            assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
        });

        // Attach policies to the role for DynamoDB access
        lambdaRole.addToPolicy(new iam.PolicyStatement({
            actions: ['dynamodb:GetItem', 'dynamodb:PutItem', 'dynamodb:UpdateItem', 'dynamodb:DeleteItem', 'dynamodb:Query', 'dynamodb:Scan'],
            resources: [
                cdk.Fn.importValue('TestEventsTableArn'),
                cdk.Fn.importValue('LastTestEventsTableArn'),
                cdk.Fn.importValue('BehaviorsTableArn'),
            ],
        }));

        // Environment variables for the Lambda function
        const environmentVariables = {
            TEST_EVENTS_TABLE_NAME: cdk.Fn.importValue('TestEventsTableName'),
            LAST_TEST_EVENTS_TABLE_NAME: cdk.Fn.importValue('LastTestEventsTableName'),
            BEHAVIORS_TABLE_NAME: cdk.Fn.importValue('BehaviorsTableName'),
        };

        // Define the Lambda function
        this.lambda = new lambda.Function(this, 'PromptManagementHandler', {
            runtime: lambda.Runtime.PYTHON_3_11,
            code: lambda.Code.fromAsset('../backend'),
            handler: 'src.lambda_prompt_management_handler.lambda_handler',
            memorySize: 128,
            timeout: cdk.Duration.minutes(15),
            environment: environmentVariables,
            role: lambdaRole, // Attach the IAM role to the Lambda function
        });

        // Output the Lambda function ARN
        new cdk.CfnOutput(this, 'PromptManagementHandlerLambdaArn', {
            value: this.lambda.functionArn,
            exportName: 'PromptManagementHandlerLambdaArn',
        });
    }
}