import * as cdk from 'aws-cdk-lib';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import { Construct } from 'constructs';

export class DynamoDbStack extends cdk.Stack {

    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id);
        const testEventsTable = this.createDynamoDbTable('LamoomFlowPromptTesternewTestEvents', 'lambda_name', 'timestamp', {});
        const lastTestEventsTable = this.createDynamoDbTable('LamoomFlowPromptTesternewLastTestEvents', 'lambda_name', 'test_case', {});
        const behaviorsTable = this.createDynamoDbTable('Behaviors', 'behavior_id', 'timestamp', {});

        // Output table names and ARNs for cross-stack reference
        this.outputTableResources(testEventsTable);
        this.outputTableResources(lastTestEventsTable);
        this.outputTableResources(behaviorsTable);
    }

    private createDynamoDbTable(tableName: string, partitionKey: string, sortKey: string, props: {
        minWriteCapacity?: number,
        maxWriteCapacity?: number,
        minReadCapacity?: number,
        maxReadCapacity?: number,
        typeSk?: dynamodb.AttributeType,
        additional_indexes?: dynamodb.GlobalSecondaryIndexProps[],
    }): dynamodb.Table {
        const table = new dynamodb.Table(this, tableName, {
            partitionKey: { name: partitionKey, type: dynamodb.AttributeType.STRING },
            sortKey: { name: sortKey, type: props.typeSk || dynamodb.AttributeType.STRING},
            billingMode: dynamodb.BillingMode.PROVISIONED,
            tableName: tableName,
            readCapacity: 1,
            writeCapacity: 1,
        });
        table.autoScaleWriteCapacity({
            minCapacity: props.minWriteCapacity || 1,
            maxCapacity: props.maxWriteCapacity || 10,
        });
        table.autoScaleReadCapacity({
            minCapacity: props.minReadCapacity || 1,
            maxCapacity: props.maxReadCapacity || 10,
        });

        if (props.additional_indexes) {
            props.additional_indexes.forEach((index) => {
                table.addGlobalSecondaryIndex(index);
            });
        }

        return table;
    }

    private outputTableResources(table: dynamodb.Table) {
        const tableName = table.tableName;
        const tableArn = table.tableArn;

        new cdk.CfnOutput(this, `${tableName}NameOutput`, {
            value: tableName,
            exportName: `${tableName}Name`,
        });

        new cdk.CfnOutput(this, `${tableName}ArnOutput`, {
            value: tableArn,
            exportName: `${tableName}Arn`,
        });
    }
}