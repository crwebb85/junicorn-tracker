import * as cdk from 'aws-cdk-lib';

import { BootstrapStack } from '../src/bootstrap-stack';

const app = new cdk.App();
new BootstrapStack(app, 'BootstrapStack', {
  githubOrganisation: 'crwebb85',
  repository: 'junicorn-tracker',
  branch: 'main',
});
