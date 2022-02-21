import * as dotenv from 'dotenv';
import * as path from 'path';

import { Architecture, Runtime } from 'aws-cdk-lib/aws-lambda';
import { Duration, Stack, StackProps } from 'aws-cdk-lib';
import { Rule, Schedule } from 'aws-cdk-lib/aws-events';

import { Construct } from 'constructs';
import { LambdaFunction } from 'aws-cdk-lib/aws-events-targets';
import { PythonFunction } from '@aws-cdk/aws-lambda-python-alpha';

interface JunicornTrackerLambdaConfig {
  webdavDomainName: string;
  webdavUsername: string;
  webdavPassword: string;
  webdavUploadPath: string;
  instagramUsername: string;
  instagramPassword: string;
}
export class JunicornTrackerStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    dotenv.config();

    const env: JunicornTrackerLambdaConfig = {
      webdavDomainName: process.env['WEBDAV_DOMAIN_NAME'] ?? '',
      webdavUsername: process.env['WEBDAV_USERNAME'] ?? '',
      webdavPassword: process.env['WEBDAV_PASSWORD'] ?? '',
      webdavUploadPath: process.env['WEBDAV_UPLOAD_PATH'] ?? '',
      instagramUsername: process.env['INSTAGRAM_USERNAME'] ?? '',
      instagramPassword: process.env['INSTAGRAM_PASSWORD'] ?? '',
    };

    const junicornTrackerLambda = new PythonFunction(this, 'InstagramTreackerLambda', {
      entry: path.join(__dirname, 'lambda'),
      runtime: Runtime.PYTHON_3_9,
      index: 'index.py',
      handler: 'handler',
      architecture: Architecture.ARM_64,
      environment: {
        region: Stack.of(this).region,
        availabilityZones: JSON.stringify(Stack.of(this).availabilityZones),
        ...env,
      },
    });

    const cronRule = new Rule(this, 'Scheduler', {
      schedule: Schedule.rate(Duration.hours(12)),
    });
    cronRule.addTarget(new LambdaFunction(junicornTrackerLambda));
  }
}
