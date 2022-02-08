import * as path from "path";

import { Architecture, Code, Function, Runtime } from "aws-cdk-lib/aws-lambda";
import { Stack, StackProps } from 'aws-cdk-lib';

import { Construct } from 'constructs';

export class JunicornTrackerStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const junicornTrackerLambda = new Function(this, "InstagramTrackerLambda", {
      code: Code.fromAsset(path.join(__dirname, "lambda")),
      handler: "index.main",
      runtime: Runtime.PYTHON_3_6,
      architecture: Architecture.ARM_64,
    });
    
  }
}
