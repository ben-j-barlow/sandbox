# Asset Bundle Deployment

## Key Commands

* `databricks bundle deploy -p <target>`: uploads source code to `.bundle` directory on DBX workspace and creates the app, but does not point the app to the source code
* `databricks bundle run hello_world_app -p <target>`: starts the app (i.e. provisions the compute) and deploys it, a subprocess of which is pointing the app to the source code