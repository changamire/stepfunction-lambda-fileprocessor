# Process arbitarily large newline-delimited text files on AWS

Inspired by [this article](https://www.linkedin.com/pulse/large-file-processing-csv-using-aws-lambda-step-functions-nacho-coll/) - sometimes you may find the need to process very large newline-delimited text files within AWS - examples include large CSV files, or [jsonl](http://jsonlines.org/) files. Or your files may not even be that large but you may want to do something time consuming or computationally intensive with each line. Either way, the [limits](https://docs.aws.amazon.com/lambda/latest/dg/limits.html) imposed on lambdas, although recently increased, may preclude you from being able to use a single lambda invocation to process your very large file. 

Enter AWS [step functions](https://aws.amazon.com/step-functions/) - a very simple but powerful way to stitch cloud services together and orchestrate more complex workflows from serverless components. This project uses a step function and a simple lambda to process, line by line, an arbitarily sized file of newline-delimited text.

To use this, you'll need an AWS account and the CLI installed and configured with an access key. In addition, you'll need the [serverless framework](https://serverless.com/) and [npm](https://www.npmjs.com/) installed. 

Then follow these steps,

Clone the repository

```
https://github.com/changamire/stepfunction-lambda-fileprocessor.git
```

Install serverlerless plugins 

```
npm install
```

Deploy to the cloud

```
sls deploy
```

One the application is deployed, the step-function can be started, passing it an event containing details of the file in S3 to be processed in the structure of an [S3 event](https://docs.aws.amazon.com/AmazonS3/latest/dev/notification-content-structure.html), e.g.:-

```json
{
  "Records": [
    {
      "s3": {
        "object": {
          "key": "BigBoy.csv"
        },
        "bucket": {
          "name": "my-bucket"
        }
      }
    }
  ]
}
```