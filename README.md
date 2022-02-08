# Junicorn Tracker (An Instagram Tracker)

Currently in developement.

## Description
Tracks and download new stories and posts from Instagram. Stores the files on any WebDAV compatible fileserver (only tested for [Nextcloud](https://nextcloud.com/)).

## Architecture 

Deployed as AWS CDK stack (written in Typescript) which creates a AWS Lambda (written in python). The lambda downloads the posts and stories from instagram and uploads them to a WebDAV compatible fileserver. The lambda is scheduled to run twice a day. 


## Useful commands

 * `yarn build`     compile typescript to js
 * `yarn watch`     watch for changes and compile
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk synth`       emits the synthesized CloudFormation template
