
# xmigrate.cloud, an opensource project for cloud migration

**xmigrate.cloud**, which is pronounced as *cross-migrate.cloud*, is an opensource project for migrating your infrastructure.
Migration can be done from DC to DC, DC to cloud, Cloud to DC, and Cloud to Cloud.

> Scope of this tool is limited to migration of VMs across any cloud/on-prem to cloud environment.

## Current release

We have shipped xmigrate with the below features in our latest [release](https://hub.docker.com/r/xmigrate/xmigrate);

- Environment discovery
- Automatic network creation and server deployment
- Multiple cloud environment support
- Agentless discovery and migration
- Any to AWS server migration*
- Any to GCP server migration*
- Any to Azure server migration*
- Migration of servers with multiple disks

> 💡 *As a user you need to ensure the server which you are migrating is eligible to be migrated to the target cloud. We will add precheck scripts in discovery phase before preparing the server for migration in coming releases.

## Tech stack

xmigrate is built on the below techstack;

- FastAPI (Python web framework)
- Ansible
- PostgreSQL

xmigrate runs as a container in your local machine.
All the web-services and payloads are written in Python.
Ansible is used to prepare the servers ready for migration and PostgreSQL DB is used to store user, project, cloud environment and other metadata related to the VM which needs to be migrated.

## Future Roadmap

- Support for more OS versions
- Support for GPT boot volume to AWS

## 🚀How to deploy?

```bash
git clone https://github.com/xmigrate/xmigrate.git
cd xmigrate
```

After cloning the repository and entering it, open the `docker-compose.yaml` file and replace the *\<server-ip\>* placeholder in the line `BASE_URL: http://<server-ip>/api` with your server ip address.

You can choose which version of the app to run by changing the version number in the image parameter of app service: `image: xmigrate/xmigrate:v0.1.6`.

Alternately you can choose to build the app locally by removing the image specification and adding `build: .` in place. Be careful that this could cause the app to build with unreleased changes.

Once you are satisfied with the initial setup, you can run the below command and access xmigrate on `http://localhost:80`;

```bash
docker compose up -d
```

## OS compatiability matrix

We currently support servers of below OS versions*;

|           | Redhat 7 | Redhat 8 | CentOS 7 | Ubuntu 16.04 | Ubuntu 18.04 | Ubuntu 20.04 |
|-----------|----------|----------|----------|--------------|--------------|--------------|
| **AWS**   |  ✅      |   ✅    |    ✅    |     ✅       |     ✅      |      ✅        |
| **Azure** |  ✅      |   ✅    |    ✅    |     ✅       |     ✅      |      ✅      |
| **GCP**   |  ✅      |   ✅    |    ✅    |     ✅       |     ✅      |      ✅      |

> 💡 Make sure your `/etc/fstab` entries looks like this
`UUID=d35fe619-1d06-4ace-9fe3-169baad3e421 /                       xfs     defaults,discard        1 1`

We will be adding support for more OS soon.

> ℹ *We are aware of and working hard to find a quick solution to some issues that prevent vm connectivity after migrations of Azure to AWS, Azure to GCP, and GCP to Azure. In the meantime, all other combinations with our supported providers can be used without issues.

Stay tuned for more updates. Join our [community](https://xmigrate.slack.com/) and start collaborating 🎉

## License

[xmigrate](https://github.com/iamvishnuks/xmigrate) by [Vishnu KS](https://iamvishnuks.com/) is licensed under [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0)

<a rel="license" href="https://creativecommons.org/licenses/by-nc-nd/4.0"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc-nd/4.0/88x31.png" /></a>
