import * as path from 'path';

import { Architecture, Code, Function, Runtime } from 'aws-cdk-lib/aws-lambda';
import { Duration, Stack, StackProps } from 'aws-cdk-lib';
import { Rule, Schedule } from 'aws-cdk-lib/aws-events';

import { Construct } from 'constructs';
import { LambdaFunction } from 'aws-cdk-lib/aws-events-targets';

export class JunicornTrackerStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const junicornTrackerLambda = new Function(this, 'InstagramTrackerLambda', {
      code: Code.fromAsset(path.join(__dirname, 'lambda')),
      handler: 'index.handler',
      runtime: Runtime.PYTHON_3_9,
      architecture: Architecture.ARM_64,
    });

    const cronRule = new Rule(this, 'Scheduler', {
      schedule: Schedule.rate(Duration.hours(12)),
    });
    cronRule.addTarget(new LambdaFunction(junicornTrackerLambda));
  }
}
