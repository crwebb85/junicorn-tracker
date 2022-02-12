import * as cdk from 'aws-cdk-lib';

import { JunicornTrackerStack } from '../src/junicorn-tracker-stack';

const app = new cdk.App();
new JunicornTrackerStack(app, 'JunicornTrackerStack');
