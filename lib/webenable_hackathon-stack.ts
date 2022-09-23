import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { Code, Function, Handler, Runtime, LayerVersion } from 'aws-cdk-lib/aws-lambda';
import { Bucket, EventType } from 'aws-cdk-lib/aws-s3';
import { BundlingOutput, DockerImage, Duration } from 'aws-cdk-lib';
import { LambdaDestination } from 'aws-cdk-lib/aws-s3-notifications';
import { PythonFunction, PythonLayerVersion, BundlingOptions } from '@aws-cdk/aws-lambda-python-alpha';

export class WebenableHackathonStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const bucket = Bucket.fromBucketName(this, "Bucket", "tdv-birds");
    
    const func_layer = new LayerVersion(this, "FunctionLayer", {
      code: Code.fromAsset("./src/birdid_layer/python_2.7.0.zip"),
      compatibleRuntimes: [Runtime.PYTHON_3_9],
    });

    const model_layer = new LayerVersion(this, "ModelLayer", {
      code: Code.fromAsset("./src/birdid_model"),
      compatibleRuntimes: [Runtime.PYTHON_3_9],
    })

    const func_lite = new Function(this, "FunctionLite", {
      code: Code.fromAsset("./src/birdid_noimage"),
      runtime: Runtime.PYTHON_3_9,
      memorySize: 4096,
      timeout: Duration.minutes(1),
      handler: 'handler.handler',
      layers: [
        func_layer,
        model_layer
      ],
    })

    bucket.grantReadWrite(func_lite);

    bucket.addEventNotification(EventType.OBJECT_CREATED, new LambdaDestination(func_lite));
  }
}
