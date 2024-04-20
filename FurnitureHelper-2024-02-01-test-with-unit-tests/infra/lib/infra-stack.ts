import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as opensearch from 'aws-cdk-lib/aws-opensearchservice';
import * as secretsmanager from 'aws-cdk-lib/aws-secretsmanager';

export class ReusableResourcesStack extends cdk.Stack {
    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);

        const table = new dynamodb.Table(this, 'PreferencesTable', {
            partitionKey: { name: 'user_id', type: dynamodb.AttributeType.STRING },
            // additional table configuration
        });

        new cdk.CfnOutput(this, 'DynamoDbTableArn', {
            value: table.tableArn,
            exportName: 'DynamoDbTableArn',
        });

        const domain = new opensearch.Domain(this, 'PreferencesDomain', {
            // domain configuration
        });

        new cdk.CfnOutput(this, 'OpenSearchDomainArn', {
            value: domain.domainArn,
            exportName: 'OpenSearchDomainArn',
        });

        const openAiApiKeySecret = new secretsmanager.Secret(this, 'OpenAiApiKeySecret', {
            // secret configuration
        });

        new cdk.CfnOutput(this, 'OpenAiApiKeySecretArn', {
            value: openAiApiKeySecret.secretArn,
            exportName: 'OpenAiApiKeySecretArn',
        });
    }
}