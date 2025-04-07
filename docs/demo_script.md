# Snowplow Signals CLI Tutorial

## Overview
This tutorial will guide you through using the Snowplow Signals SDK CLI tool to:
1. Test API connectivity
2. Initialize dbt projects
3. Generate dbt models and assets

## Prerequisites
Before starting, ensure you have:
- Python 3.8+ installed
- Snowplow Signals SDK installed
- Valid API credentials:
  - API URL
  - API Key
  - API Key ID
  - Organization ID

## Setting Up Environment Variables
For convenience, you can set up your API credentials as environment variables. This allows you to run commands without specifying credentials each time:

```bash
export SNOWPLOW_API_URL="YOUR_API_URL"
export SNOWPLOW_API_KEY="YOUR_API_KEY"
export SNOWPLOW_API_KEY_ID="YOUR_API_KEY_ID"
export SNOWPLOW_ORG_ID="YOUR_ORG_ID"
export SNOWPLOW_REPO_PATH="./my_snowplow_project"
```

## Step 1: Testing Connection
Let's start by verifying that we can connect to the Snowplow Signals services:

```bash
snowplow-batch-autogen test-connection \
  --api-url "YOUR_API_URL" \
  --api-key "YOUR_API_KEY" \
  --api-key-id "YOUR_API_KEY_ID" \
  --org-id "YOUR_ORG_ID" \
  --verbose
```

If you've set up environment variables, you can simply run:
```bash
snowplow-batch-autogen test-connection --verbose
```

This command will:
- Test authentication service connectivity
- Check API service health
- Verify all dependencies
- Provide detailed status information

Expected output:
```
🔐 Testing authentication service...
✅ Authentication service is healthy

🌐 Testing API service...
✅ API service is healthy
📊 Dependencies status:
   ✅ database: ok
   ✅ cache: ok
   ✅ storage: ok

✨ All services are operational!
```

## Step 2: Initializing a Project
Now, let's create a new dbt project:

```bash
snowplow-batch-autogen init \
  --api-url "YOUR_API_URL" \
  --api-key "YOUR_API_KEY" \
  --api-key-id "YOUR_API_KEY_ID" \
  --org-id "YOUR_ORG_ID" \
  --repo-path "./my_snowplow_project" \
  --verbose
```

With environment variables set:
```bash
snowplow-batch-autogen init --verbose
```

This will:
- Create a new dbt project structure
- Set up base configuration files
- Initialize necessary directories

Expected output:
```
Initializing dbt project(s) in ./my_snowplow_project
✅ Successfully initialized dbt project(s)
```

## Step 3: Generating Models
Finally, let's generate the dbt models:

```bash
snowplow-batch-autogen generate \
  --api-url "YOUR_API_URL" \
  --api-key "YOUR_API_KEY" \
  --api-key-id "YOUR_API_KEY_ID" \
  --org-id "YOUR_ORG_ID" \
  --repo-path "./my_snowplow_project" \
  --verbose
```

With environment variables:
```bash
snowplow-batch-autogen generate --verbose
```

This will:
- Generate data models
- Create macros
- Set up configuration files
- Update existing files if needed

Expected output:
```
🛠️ Generating dbt models in ./my_snowplow_project
✅ Successfully generated dbt models
```

## Advanced Features

### Initializing Specific Views
You can initialize a specific attribute view:

```bash
snowplow-batch-autogen init \
  --view-name "user_attributes" \
  --view-version 1 \
  --verbose
```

### Updating Existing Models
To update existing models:

```bash
snowplow-batch-autogen generate \
  --update \
  --verbose
```

## Troubleshooting

### Common Issues
1. **Authentication Errors**
   - Verify API credentials
   - Check network connectivity
   - Ensure API key has correct permissions

2. **Project Initialization Issues**
   - Check repository path permissions
   - Verify sufficient disk space
   - Ensure directory is not locked

3. **Model Generation Problems**
   - Check API service health
   - Verify schema compatibility
   - Ensure proper project structure

### Debugging Tips
- Use `--verbose` flag for detailed logs
- Check API service health before operations
- Verify project structure after initialization

## Best Practices
1. Always test connection before operations
2. Use version control for generated projects
3. Keep API credentials secure
4. Regularly update generated models
5. Document any custom modifications

## Next Steps
After completing the tutorial, you can:
1. Review generated dbt models
2. Customize configurations
3. Set up CI/CD pipelines
4. Implement monitoring
5. Create custom macros

## Support
For additional help:
- Check the official documentation
- Contact Snowplow support
- Join the community forum
- Review GitHub issues 