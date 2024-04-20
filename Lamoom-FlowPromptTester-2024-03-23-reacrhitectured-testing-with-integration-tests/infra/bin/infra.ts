import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { InfraStack } from '../lib/infra-stack';
import { PromptTestingHandlerStack } from '../lib/lambda_prompt_testing_handler';

const app = new cdk.App();
new InfraStack(app, 'LamoomFlowPromptTesternew', {
    // Stack properties as needed
});

// Add the PromptTestingHandlerStack to the CDK app
new PromptTestingHandlerStack(app, 'PromptTestingHandlerStack', {
    env: {
        account: process.env.CDK_DEFAULT_ACCOUNT,
        region: process.env.CDK_DEFAULT_REGION,
    },
});