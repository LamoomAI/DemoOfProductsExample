
import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import {Construct} from 'constructs';


export class PromptTestingHandlerStack extends cdk.Stack {
    public readonly lambda: lambda.Function;

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);
    const accountId = process.env.CDK_DEFAULT_ACCOUNT as string;
    const accountSettings = this.node.tryGetContext(accountId);
    const layer = new lambda.LayerVersion(this, 'PoetryDependenciesLayer', {
      code: lambda.Code.fromAsset('../backend/layer.zip'),
      compatibleRuntimes: [lambda.Runtime.PYTHON_3_11], // adjust as needed
      license: 'Apache-2.0',
      description: 'A layer to hold the poetry dependencies',
    });
    const environmentVariables = {
        IS_QA_ENV: accountSettings.is_qa_env,
        TEST_EVENTS_TABLE_NAME: 'LamoomFlowPromptTesternewTestEvents',
        LAST_TEST_EVENTS_TABLE_NAME: 'LamoomFlowPromptTesternewLastTestEvents',
    };
    this.lambda = new lambda.Function(this, 'PromptTestingHandler', {
      runtime: lambda.Runtime.PYTHON_3_11,
      code: lambda.Code.fromAsset('../backend'), // path to the lambda code
      handler: 'src.lambda_prompt_testing_handler.lambda_handler', // specify the file and export
      memorySize: 128, // please update as needed
      timeout: cdk.Duration.minutes(15), // please update as needed
      environment: environmentVariables,
    });
    this.lambda.addLayers(layer);
    
  }
}
