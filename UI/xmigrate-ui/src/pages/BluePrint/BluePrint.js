import React, { Component } from "react";
import "./BluePrint.scss";
import {
  Container,
  Table,
  Card,
  Button,
  Form,
  Row,
  Col,
} from "react-bootstrap";
import * as icon from "react-icons/all";
import { GetServiceWithData } from "../../services/GetService";
import {
  BLUEPRINT_URL,
  BLUEPRINTNET_NETWORK_CREATE_URL,
  BLUEPRINTNET_NETWORK_GET_URL,
  BLUEPRINTNET_SUBNET_POST_URL,
  BLUEPRINTNET_HOST_GET_URL,
  BLUEPRINTNET_BUILD_POST_URL,
  BLUEPRINTNET_GET_VMS,
  BLUEPRINTNET_DELETE_NETWORK,
  BLUEPRINTNET_DELETE_SUBNET,
  BLUEPRINT_SAVE,
  BLUEPRINT_STATUS,
  BLUEPRINT_UDATE_HOST
} from "../../services/Services";
import PostService from "../../services/PostService";
import Loader from "../../components/Loader/Loader";
import NetworkTableRow from "../../components/Table/NetworkTable";
export default class BluePrint extends Component {
  constructor(props) {
    super();
    let input = {};
    this.state = {
      input: input,
      Networks: [],
      dragStart: false,
      cidr: "",
      project: props.CurrentPro.name,
      status: "loading",
      VMS: [],
      hosts: [],
      VMSSelected: "",
      hostCurrent: {},
      SubnetData: [],
      BuildStatus: false
    };
    this.handleChange = this.handleChange.bind(this);
    this.CreateSubnet = this.CreateSubnet.bind(this);
    this.DeleteNetwork = this.DeleteNetwork.bind(this);
    this.DeleteSubnet = this.DeleteSubnet.bind(this);
    this.handleVM = this.handleVM.bind(this);
    this.drag = this.drag.bind(this);
    this.allowDrop = this.allowDrop.bind(this);
    this.drop = this.drop.bind(this);
    this.getStatus = this.getStatus.bind(this)
  }

  async GettingData() {
    this.setState({
      status: "loading",
    });
    var data = {
      project: this.state.project,
    };
    // await GetServiceWithData(BLUEPRINTNET_NETWORK_GET_URL, data).then((res) => {
    //   NetworksData = JSON.parse(res.data);
    //   NetworksData.forEach((Network) => {
    //     Network["subnet"] = [];
    //   });
    //   console.log("The Networks Loading", NetworksData);
    // });

    let VMSDATA;
    let hostCurrents = [];
    //Getting the VMS  Details------------
    await GetServiceWithData(BLUEPRINTNET_GET_VMS, data).then((res) => {
      VMSDATA = res.data.machine_types;
      console.log("Machine Types", VMSDATA);
    });

    //Gettin the Details of Current Host
    let NetworksDatas;
    await GetServiceWithData(BLUEPRINTNET_HOST_GET_URL, data).then((res) => {
      console.log("Response Data of New Blueprint host", res.data.networks);
      NetworksDatas = res.data.networks;
      NetworksDatas.map((Network, index) => {
        Network.subnets.map((subnet, index) => {
          subnet.hosts.map((host, index) => {
            let hostCurrent = {};
            hostCurrent["hostname"] = host.host;
            hostCurrent["type"] = subnet.subnet_type;
            hostCurrent["subnet"] = host.subnet;
            hostCurrent["machine_type"] = host.machine_type;
            hostCurrents.push(hostCurrent);
          });
        });
      });
    });

    //Setting the State
    this.setState({
      Networks: NetworksDatas,
      VMS: VMSDATA,
      hostCurrents: hostCurrents,
      status: "loaded",
    });
  }

  async componentDidMount() {
    var data = {
      project: this.state.project,
    };
    await GetServiceWithData(BLUEPRINT_URL, data).then((res) => {
      console.log("Logging Blueprint url details", res.data);
      var dataBlurprint = JSON.parse(res.data);
      dataBlurprint.map((data, index) =>
        this.state.hosts.push({
          id: index,
          _id: data._id,
          hostname: data.host,
          ip: data.ip,
          subnet: data.subnet,
          network: data.network,
          cpu: data.cpu_model,
          core: data.cores,
          ram: data.ram,
          disk: data.disk,
        })
      );
    });

    //Getting the Network Data
    this.GettingData();
  }

  //Function for Create Network*********************
  async _createBluePrint() {
    var data = {
      cidr: this.state.input["NetworkCIDR"],
      project: this.state.project,
      name: this.state.input["NetworkName"],
    };
    console.log("the data passsed to create network url", data);
    await PostService(BLUEPRINTNET_NETWORK_CREATE_URL, data).then((res) => {
      console.log("data fot as response", res.data);
    });
    var dataGet = {
      project: this.state.project,
    };
    let NetworksData = this.state.Networks;
    await GetServiceWithData(BLUEPRINTNET_NETWORK_GET_URL, dataGet).then(
      (res) => {
        var NetworksDataServer = JSON.parse(res.data);
        NetworksDataServer.forEach((Network) => {
          if (this.state.input["NetworkName"] === Network.nw_name) {
            Network["subnets"] = [];
            NetworksData.push(Network);
          }
        });
        console.log("the Networks Loading", NetworksData);
        this.setState({ Networks: NetworksData });
      }
    );
  }

  //Creating Subnet in Network-------------------------------------------------------------------------
  async CreateSubnet(NameNetwork) {
    const indexNetwork = this.state.Networks.findIndex(
      (Network) => Network.nw_name === NameNetwork
    );
    console.log(indexNetwork);
    var data = {
      cidr: this.state.input["SubnetCidr"],
      project: this.state.project,
      nw_name: NameNetwork,
      nw_type: this.state.input["Security"] || "Public",
      name: this.state.input["SubnetName"],
    };
    console.log("Data Response to Subnet", data);
    //Posting Subnet Details
    await PostService(BLUEPRINTNET_SUBNET_POST_URL, data).then((res) => {
      console.log("data from response of subnet post", res.data);
    });

    this.GettingData();
  }

  //Deleteing Network Detaisls--------------------------------------------------------------------------------
  async DeleteNetwork(NameNetwork) {
    console.log("Delete");
    var data = {
      project: this.state.project,
      nw_name: NameNetwork,
    };
    //Delete Network Details------------
    await GetServiceWithData(BLUEPRINTNET_DELETE_NETWORK, data).then((res) => {
      console.log("Delete Data From Host", res.data);
    });
    var NetworksData = this.state.Networks;
    var i;
    NetworksData.map((Network, index) => {
      if (Network.nw_name === NameNetwork) {
        i = index;
      }
    });
    if (i > -1) {
      NetworksData.splice(i, 1);
    }

    console.log("After Deleteing Network Data", NetworksData);
    this.setState({
      Networks: NetworksData,
    });
  }

  //Deleteing Subnet Detaisls--------------------------------------------------------------------------------
  async DeleteSubnet(subnetname, nw_name) {
    console.log("Deleting Subent");
    var data = {
      project: this.state.project,
      subnet_name: subnetname,
      nw_name: nw_name,
    };
    await GetServiceWithData(BLUEPRINTNET_DELETE_SUBNET, data).then((res) => {
      console.log("Delete Data From Host", res.data);
    });
    this.GettingData();
  }

  //Handling Changes-----------------------------------------------------------------------------------
  handleChange(event) {
    let input = this.state.input;
    input[event.target.name] = event.target.value;
    this.setState({
      input,
    });
  }

  //Handling Change Of VM--------------------------------------------------------------------------------
  handleVM(event, host) {
    // console.log(event.target.value);
    // console.log(host);
    let hostCurrent = this.state.hostCurrents;
    hostCurrent.map((hostCur, index) => {
      if (hostCur.hostname === host.host) {
        hostCur["machine_type"] = event.target.value;
      }
    });
    // console.log("The hostCurrent",hostCurrent);
    this.setState({
      hostCurrents: hostCurrent,
    });
  }

  //Creating Build-------------------------------------------------------------------------
  async _createBuild() {
    let data = {
      project: this.state.project,
    };
    this.setState({ BuildStatus: true})
    console.log("Building");
    await PostService(BLUEPRINTNET_BUILD_POST_URL, data).then((res) => {
      console.log("data from response of Build post", res.data);
      var interval = setInterval(this.getStatus, 3000);
      this.setState({ interval: interval });
    });
  }
  getStatus() {
    let data1 = {
      project: this.state.project,
    };
    GetServiceWithData(BLUEPRINT_STATUS, data1).then((res) => {
      console.log("Response For Status",res);
      let flag;
      let NetworksData = this.state.Networks;
      //Setting the host status
      NetworksData.map((Network, index) => {
        Network.subnets.map((subnet, index) => {
          subnet.hosts.map((host, index) => {
            res.data.map((hostRes, index) => {
              if (host.host === hostRes.host) {
                host["status"] = hostRes.status;
                if (parseInt(hostRes.status) <100) {
                  flag = false;
                }
                else{
                  flag = true;
                }
              }
            });
          });
        });
      });
      if (flag) {
        clearInterval(this.state.intervalId);
        this.setState({ BuildStatus: false})
      }
      this.setState({
        Networks: NetworksData,
      });
    });
  }

  //Creating SaveNetwork-----------------------------------------------------------------
  async _SaveBuild() {
    console.log(
      "Here the data for host Current is saved",
      this.state.hostCurrents
    );
    let hostData = this.state.hostCurrents
    hostData.map((host,index)=>{
      if(host.type === "Public" || host.type === "True"  ){
        host["type"] = "True"
      }
      else{
        host["type"] = "False"
      }
    });
    var data = {
      project: this.state.project,
      machines: hostData,
    };
    console.log(data);
    await PostService(BLUEPRINT_SAVE, data).then((res) => {
      console.log("data from response of Build post", res.data);
    });
  }

  //--------------Reset the Network Table
  async _Reset() {
    console.log("Reseting....");
    var NetworksData = this.state.Networks;
    NetworksData.map((Network, index) => {
      let data = {
        project: this.state.project,
        nw_name: Network.nw_name,
      };
      GetServiceWithData(BLUEPRINTNET_DELETE_NETWORK, data).then((res) => {
        console.log("Delete Data From Host", res.data);
      });
    });
    //Getting all details if any
    this.GettingData();
  }

  // Draging and Drop
  drag(ev, host, index, subnetname, nw_name) {
    let data = {
      host: host,
      index: index,
      ChangeSubnet: subnetname,
      ChangeNetwork: nw_name,
    };
    console.log("On drag",data);
    ev.dataTransfer.setData("TransferJson", JSON.stringify(data));
  }

  allowDrop(ev) {
    ev.preventDefault();
  }

  drop(ev, subnetname, nw_name) {
    ev.preventDefault();
    let SamePlace = false;
    var data = JSON.parse(ev.dataTransfer.getData("TransferJson"));
       //Checking if in same place
    if(nw_name === data.ChangeNetwork && subnetname === data.ChangeSubnet ){
        console.log("Same Place");
        SamePlace = true;
    }
    if(SamePlace === false){
    console.log("On Drop",);
    console.log(subnetname);
    console.log(nw_name);
    var NetworksData = this.state.Networks;
    NetworksData.map((Network, index) => {
      if (Network.nw_name === data.ChangeNetwork) {
        Network.subnets.map((subnet, index) => {
          if (subnet.name === data.ChangeSubnet) {
            subnet.hosts.splice(data.index, 1);
          }
        });
        if (Network.nw_name === nw_name) {
          Network.subnets.map((subnet, index) => {
            if (subnet.name === subnetname) {
              data.host["subnet"] = subnet.cidr;
              subnet.hosts.push(data.host);
            }
          });
        }

      } else if (Network.nw_name === nw_name) {
        Network.subnets.map((subnet, index) => {
          if (subnet.name === subnetname) {
            data.host["subnet"] = subnet.cidr;
            subnet.hosts.push(data.host);
          }
        });
      } else {
      }
    });

    var data1 = {
      project: this.state.project,
      machines:[data.host]
    }
    console.log("data passinf to the url",data1);
    PostService(BLUEPRINT_UDATE_HOST, data1).then((res) => {
      console.log("After Drag and drop", res.data);
    });
    this.setState({
      Networks: NetworksData,
    });
    this.GettingData();
  }
  
  }

  render() {
    const Networks = this.state.Networks;
    const isLoadingNetwork = Networks.length === 0;
    if (this.state.status === "loading") {
      return (
        <Container>
          <Loader />
        </Container>
      );
    } else {
      return (
        <div className="BluePrint media-body background-primary">
          <Container className="py-5 ">
            <h4 className="p-0 m-0">Blueprint</h4>
            <Card className="mt-4 p-2">
              <Card.Header className="bg-white">Discovered Hosts</Card.Header>
              <Card.Body>
                <Table responsive borderless>
                  <thead>
                    <tr>
                      <th>#</th>
                      <th>Hostname</th>
                      <th>IP</th>
                      <th>Subnet</th>
                      <th>Network</th>
                      <th>CPU Model</th>
                      <th>Core</th>
                      <th>Ram</th>
                      <th>Disk</th>
                    </tr>
                  </thead>
                  <tbody>
                    {this.state.hosts.map((data, index) => (
                      <tr key={index}>
                        <td>{data.id}</td>
                        <td>{data.hostname}</td>
                        <td>{data.ip}</td>
                        <td>{data.subnet}</td>
                        <td>{data.network}</td>
                        <td>{data.cpu}</td>
                        <td>{data.core}</td>
                        <td>{data.ram}</td>
                        <td>{data.disk}</td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              </Card.Body>
            </Card>



            {/* HereTable */}

            <Card className="mt-4 p-2 blurprintTable">
              <Card.Header className="bg-white d-flex">
                <Form className="">
                  <Form.Group controlId="select-type">
                    <Row>
                      <Col>
                        <Form.Control
                          size="md"
                          onChange={this.handleChange}
                          type="text"
                          placeholder="Input Network Name"
                          name="NetworkName"
                        />
                      </Col>
                      <Col>
                        <Form.Control
                          size="md"
                          onChange={this.handleChange}
                          type="text"
                          placeholder="Input Network CIDR"
                          name="NetworkCIDR"
                        />
                      </Col>
                      <Col>
                        <Button
                          className=" media-body"
                          variant="success"
                          onClick={this._createBluePrint.bind(this)}
                        >
                          Create Network
                        </Button>
                      </Col>
                    </Row>
                  </Form.Group>
                </Form>
              </Card.Header>

              <Card.Body>
                <Container fluid className="blueprint-edit-table">
                  <Table className="bordered hover">
                    <thead>
                      <tr>
                        <th>#</th>
                        <th>NETWORK</th>
                        <th>CIDR</th>
                        <th></th>
                      </tr>
                    </thead>

                    {isLoadingNetwork ? (
                      <tbody>
                        <tr>
                          <td colSpan={6} className="text-center">
                            <em className="text-muted">
                              No Network Data Avaialble...
                            </em>
                          </td>
                        </tr>
                      </tbody>
                    ) : (
                      this.state.Networks.map((NetworkData, index) => (
                        <NetworkTableRow
                          key={index}
                          index={index + 1}
                          Network={NetworkData}
                          VMS={this.state.VMS}
                          handleChange={this.handleChange}
                          CreateSubnet={this.CreateSubnet}
                          DeleteNetwork={this.DeleteNetwork}
                          DeleteSubnet={this.DeleteSubnet}
                          handleVM={this.handleVM}
                          drag={this.drag}
                          dragStart={this.state.dragStart}
                          allowDrop={this.allowDrop}
                          drop={this.drop}
                        />
                      ))
                    )}
                  </Table>
                </Container>
              </Card.Body>
            </Card>
            <div className="mt-4 d-flex justify-content-between">
              <Button
              variant="success"
                className="media-body py-3 mr-40px text-success bt-main"
                onClick={this._SaveBuild.bind(this)}
                disabled={this.state.BuildStatus}
                size="lg"
              >
                Save <icon.FiCopy />
              </Button>
              <Button
              variant="primary"
                className="media-body py-3 mr-40px text-primary  bt-main"
                onClick={this._createBuild.bind(this)}
                disabled={this.state.BuildStatus}
                size="lg"
              >
                Build <icon.BsPlay />
              </Button>
              <Button
              variant="danger"
                className="media-body py-3 text-danger  bt-main"
                onClick={this._Reset.bind(this)}
                disabled={this.state.BuildStatus}
                size="lg"
              >
                Reset <icon.BsArrowRepeat />
              </Button>
            </div>
          </Container>
        </div>
      );
    }
  }
}
