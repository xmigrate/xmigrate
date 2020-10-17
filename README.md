
# xmigrate.cloud, an opensource project for cloud migration
xmigrate.cloud, which pronounced as cross-migrate.cloud is an opensource project for migrating your infrastructure. 
Migration can be done from DC to DC, DC to cloud, Cloud to DC, Cloud to Cloud.

>Scope of this tool is limited to migration of VM's across any cloud/on-prem environment.

Today we have enabled the platform with the following features

- Migration of Ubuntu VM's from anywhere to Azure
- Environment discovery
- Automatic network creation and server deployment
- Agentless discovery and migration


## Tech stack
xmigrate is build on below techstack
- Quart python web framework
- Ansible
- Mongodb

xmigrate is a web application which run as a container in your local machine. 

All the web-services and payloads are written in python. 
Ansible is used to prepare the servers ready for migration. MongoDB is used to store user, project, cloud environment and other metadata related to the VM which needs to be migrated.

## Future roadmap

We are passionately working towards the completion of xmigrate project to have the following features,

- Any to AWS server migration
- Any to GCP server migration
- Any to Azure server migration
- Support for following linux distros
  - Redhat
  - Fedora
  - Centos
- Multi disk support
- VM to container migration

Stay tuned for more updates. Join our [community](https://xmigrate.slack.com/) and start collaborating 🎉

## License

[xmigrate](https://github.com/iamvishnuks/xmigrate) by [Vishnu KS](https://iamvishnuks.com/) is licensed under [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0)

<a rel="license" href="https://creativecommons.org/licenses/by-nc-nd/4.0"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc-nd/4.0/88x31.png" /></a>


