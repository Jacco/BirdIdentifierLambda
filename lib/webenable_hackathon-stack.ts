import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { Code, Function, Handler, Runtime} from 'aws-cdk-lib/aws-lambda';
import { Bucket, EventType } from 'aws-cdk-lib/aws-s3';
import { Duration } from 'aws-cdk-lib';
import { LambdaDestination } from 'aws-cdk-lib/aws-s3-notifications';

export class WebenableHackathonStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const bucket = Bucket.fromBucketName(this, "Bucket", "tdv-birds");

    // The code that defines your stack goes here
    const func = new Function(this, "Function", {
      code: Code.fromAssetImage("./", {
        exclude: ["cdk.out"],
      }),
      handler: Handler.FROM_IMAGE,
      runtime: Runtime.FROM_IMAGE,
      timeout: Duration.minutes(1),
      memorySize: 4096
    })

    bucket.grantReadWrite(func);
    bucket.addEventNotification(EventType.OBJECT_CREATED, new LambdaDestination(func));
  }
}
