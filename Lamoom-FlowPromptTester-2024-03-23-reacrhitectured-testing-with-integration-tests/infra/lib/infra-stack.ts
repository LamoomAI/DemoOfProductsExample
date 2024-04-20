import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { DynamoDbStack } from './dynamodb-stack';
import { AuthenticationHandlerStack } from './lambda_authentication_handler';
import { PromptManagementHandlerStack } from './lambda_prompt_management_handler';
import { PromptTestingHandlerStack } from './lambda_prompt_testing_handler';
import * as custom_resources from 'aws-cdk-lib/custom-resources';

export class InfraStack extends cdk.Stack {
  
    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);

        const dynamoDbStack = new DynamoDbStack(this, 'DynamoDbStack');

        const authHandlerStack = new AuthenticationHandlerStack(this, 'AuthenticationHandlerStack', {});

        const authenticationHandlerLambdaArn = cdk.Fn.importValue('AuthenticationHandlerLambdaArn');

        const customResourceProvider = new cdk.custom_resources.Provider(this, 'CustomResourceProvider', {
            onEventHandler: cdk.aws_lambda.Function.fromFunctionArn(this, 'CustomResourceLambda', authenticationHandlerLambdaArn),
        });

        new cdk.CustomResource(this, 'TriggerAuthenticationHandler', {
            serviceToken: customResourceProvider.serviceToken,
            properties: {
                // Add any properties here that you want to pass to the Lambda function
            },
        });

        new cdk.aws_ssm.StringParameter(this, 'IsQaEnvParameter', {
            parameterName: 'IsQaEnv',
            stringValue: this.node.tryGetContext('is_qa_env'),
        });

        new cdk.aws_ssm.StringParameter(this, 'TestEventsTableNameParameter', {
            parameterName: 'TestEventsTableName',
            stringValue: 'LamoomFlowPromptTesternewTestEvents',
        });

        new cdk.aws_ssm.StringParameter(this, 'LastTestEventsTableNameParameter', {
            parameterName: 'LastTestEventsTableName',
            stringValue: 'LamoomFlowPromptTesternewLastTestEvents',
        });

        const promptManagementHandlerStack = new PromptManagementHandlerStack(this, 'PromptManagementHandlerStack', {
            env: {
                account: process.env.CDK_DEFAULT_ACCOUNT,
                region: process.env.CDK_DEFAULT_REGION,
            },
        });

        const promptManagementHandlerLambdaArn = cdk.Fn.importValue('PromptManagementHandlerLambdaArn');

        const customResourceProviderForPromptManagement = new cdk.custom_resources.Provider(this, 'CustomResourceProviderForPromptManagement', {
            onEventHandler: cdk.aws_lambda.Function.fromFunctionArn(this, 'CustomResourceLambdaForPromptManagement', promptManagementHandlerLambdaArn),
        });

        new cdk.CustomResource(this, 'TriggerPromptManagementHandler', {
            serviceToken: customResourceProviderForPromptManagement.serviceToken,
            properties: {
                // Add any properties here that you want to pass to the Lambda function
            },
        });

        new cdk.CfnOutput(this, 'PromptManagementHandlerLambdaArn', {
            value: promptManagementHandlerStack.lambda.functionArn,
            exportName: 'PromptManagementHandlerLambdaArn',
        });

        const promptTestingHandlerStack = new PromptTestingHandlerStack(this, 'PromptTestingHandlerStack', {
            env: {
                account: process.env.CDK_DEFAULT_ACCOUNT,
                region: process.env.CDK_DEFAULT_REGION,
            },
        });

        new cdk.CfnOutput(this, 'PromptTestingHandlerLambdaArn', {
            value: promptTestingHandlerStack.lambda.functionArn,
            exportName: 'PromptTestingHandlerLambdaArn',
        });

        new cdk.CfnOutput(this, 'MainInfraStackArn', {
            value: this.stackId,
            exportName: 'MainInfraStackArn',
        });
    }
}