# Secure Infrastructure Access (SIA) + CyberArk Identity
Agent Guard SIA allows you to generate sia-enabled postgres connection strings using stored OAuth credentials.

## Table of Contents

- [Step 1: Create an Agent Guard WebApp in CyberArk Identity Administration](#step-1-create-an-agent-guard-webapp-in-cyberark-identity-administration)
- [Step 2: Setup OpenID Connect web app](#step-2-setup-openid-connect-web-app)
    - [Settings](#settings)
    - [Trust](#trust)
    - [Tokens](#tokens)
    - [Scope](#scope)
    - [Permissions](#permissions)
- [Step 3: Log in through the Agent Guard CLI](#step-3-log-in-through-the-agent-guard-cli)
- [Step 4: Generate SIA Postgres connection string](#step-4-generate-sia-postgres-connection-string)
- [Example](#example)


## Step 1: Create an Agent Guard WebApp in CyberArk Identity Administration
On the menu to the left, Navigate to **Apps & Widgets** --> **Web Apps**
On the right, click on *Add Web Apps*

<p style="text-align: center;">
    <img src="../resources/sia/wizard.png" width="50%"/>
</p>

Click on **Custom** and then click **Add** Next to **OpenID Connect**. Next, Click on **Close** to close the new app wizard. You will then be transferred to the
new agent guard web app setup screen.

<p style="text-align: center;">
    <img src="../resources/sia/wizard2.png" width="50%"/>
</p>

## Step 2: Setup OpenID Connect web app 
Navigate through the tabs on the left and fill in the following fields:

### Settings
Fill in the following fields:

* Application ID: __agentguard

<p style="text-align: center;">
    <img src="../resources/sia/settings.png" width="50%"/>
</p>


### Trust
Copy the following fields:
* OpenID Connect client ID
* OpenID Connect issuer URL (NOTE: **WITHOUT** the /__agentguard suffix)

Create a random secret under 'OpenID Connect client secret' - We won't be using the secret, so just make sure you generate something strong enough.

Under **Service Provider Configuration**, select **Login initiated by the relying party (RP)**

Under **Authorized redirect URIs**, click on **Add** and fill in the following information:
* URL: http://localhost:5005

You will be shown a warning regarding the use of HTTP versus HTTPS - This is normal.

<p style="text-align: center;">
    <img src="../resources/sia/trust.png" width="50%"/>
</p>

### Tokens
Scroll down to **Script to set custom claims and headers**, and fill in the following script:
```javascript
setClaim('aud', '__idaptive_cybr_user_oidc');
setClaim('subdomain', TenantData.Get('CybrSubdomain'));
setClaim('tenant_id', TenantData.Get('CybrTenantID'));
```
<p style="text-align: center;">
    <img src="../resources/sia/tokens.png" width="50%"/>
</p>

### Scope
Click on the **Add** button to add the following scope:
* Name: full
* Description: full
* Above **REST Regex**, click on *Add*, and type in *.** (dot star)
* Click on **Save** 

<p style="text-align: center;">
    <img src="../resources/sia/scope1.png" width="50%"/>
</p>

### Permissions

Click on **Add**, Search for your user, select it and click on **Add**. 
Make sure you tick the 'Grant' and 'Run' permissions.

<p style="text-align: center;">
    <img src="../resources/sia/permissions.png" width="50%"/>
</p>


That's it! Your Agent Guard web app is ready to deploy. Click on **Save**. The web app will be automatically deployed.


## Step 3: Log in through the Agent Guard CLI.

Invoke the following command

```bash
agc idp login --domain <DOMAIN> --client-id <CLIENT_ID>
```

**DOMAIN** is the HOST from Step 2: Settings above (OpenID Connect issuer URL). **Do not include any prefix or suffix, just the host**
**CLIENT_ID** is the **OpenID Connect client ID**from Step2: Settings.

A complete command would look like this:

```bash
agc idp login --domain akf1234.id.cyberark.cloud --client-id 1015e2a5-db67-4c34-b244-b3962eefffff
```

Once you press enter, the browser will be opened and you will be asked to fill in your credentials. Once logged in, you should see this message,
and the agc cli will print a 'Login successful' message.

<p style="text-align: center;">
    <img src="../resources/sia/login.png" width="50%"/>
</p>

## Step 4: Generate SIA Postgres connection string

Run the following command:

```bash
agc sia postgres generate -u '<USERNAME>' -t <TENANT_ID> -h <SIA DATABASE FQDN>
```

**USERNAME** is your username (i.e john.doe@cyberark.cloud.12345)

**TENANT_ID** is your tenant ID appears infront of your CyberArk URL (i.e acme.cyberark.cloud means the tenant id is **acme**)

**SIA DATABASE FQDN** is the FQDN (Retrieve it from Secure Infrastructure Access -> Resource Management)

A complete command would look like this:

```bash
agc sia postgres generate -u 'john_doe@cyberark.cloud.12345' -t acme -h data-integration-test.cluster-c3lw4xf6ffffus-east-1.rds.amazonaws.com
```


<p style="text-align: center;">
    <img src="../resources/sia/database.png" width="50%"/>
</p>

A JIT connection string will be printed to your screen - use this connection string with a Postgres client to securely connect to your database.

## Example
First, make sure you are logged in:

```bash
agc idp login --domain akf1234.id.cyberark.cloud --client-id 1015e2a5-db67-4c34-b244-b3962eefffff
```

Next, store the connection string inside an environment variable

```bash
export SIA_CONNSTR="agc sia postgres generate -u 'john_doe@cyberark.cloud.12345' -t acme -h data-integration-test.cluster-c3lw4xf6ffffus-east-1.rds.amazonaws.com"
```

Then, Run a postgres MCP server:
```bash
npx -y @modelcontextprotocol/server-postgres $SIA_CONNSTR
```