from services.blueprint import get_blueprintid
from services.machines import get_machineid, update_vm
from services.network import get_all_networks, get_all_subnets, get_networkid
from services.project import get_projectid
from schemas.machines import VMUpdate


def update_hosts(user, project, machines, db):
    try:
        for machine in machines:
            project_id = get_projectid(user, project, db)
            blueprint_id = get_blueprintid(project_id, db)
            public_route = True if machine['public_route'] == 'Public' else False
            machine_id = get_machineid(machine["hostname"], blueprint_id, db)
            vm_data = VMUpdate(machine_id=machine_id, machine_type=machine['machine_type'], public_route=public_route, network=machine["network"])
            update_vm(vm_data, db)
        return True
    except Exception as e:
        print(repr(e))
        return False


def fetch_all_hosts(user, project, db):
    try:
        project_id = get_projectid(user, project, db)
        blueprint_id = get_blueprintid(project_id, db)
        networks = get_all_networks(blueprint_id, db)
        network_objects = []
        for network in networks:
            network_id = get_networkid(network.name, blueprint_id, db)
            subnets = get_all_subnets(network_id, db)
            network_objects.append({"nw_name": network.name, "cidr": network.cidr, 'subnets': subnets})
        return {'networks': network_objects}
    except Exception as e:
        print(str(e))

