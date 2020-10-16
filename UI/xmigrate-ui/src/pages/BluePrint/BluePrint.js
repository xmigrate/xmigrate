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
import GetService, { GetServiceWithData } from "../../services/GetService";
import {
  BLUEPRINT_URL,
  BLUEPRINTNET_NETWORK_CREATE_URL,
  BLUEPRINTNET_NETWORK_GET_URL,
  BLUEPRINTNET_SUBNET_POST_URL,
  BLUEPRINTNET_SUBNET_GET_URL,
  BLUEPRINTNET_HOST_GET_URL,
  BLUEPRINTNET_BUILD_POST_URL,
  BLUEPRINTNET_GET_VMS,
  BLUEPRINTNET_DELETE_NETWORK,
  BLUEPRINTNET_DELETE_SUBNET,
  BLUEPRINT_SAVE,
  BLUEPRINT_STATUS
} from "../../services/Services";
import PostService from "../../services/PostService";
import Loader from "../../components/Loader/Loader";
import NetworkTableRow from "../../components/Table/NetworkTable";
import { SiLetterboxd } from "react-icons/all";
export default class BluePrint extends Component {
  // Network:[
  //   subnet:[
  //     host:[],
  //   ],
  // ]
  constructor(props) {
    super();
    let input = {};
    this.state = {
      input: input,
      Networks: [],
      cidr: "",
      project: props.CurrentPro.name,
      status: "loading",
      VMS: [],
      hosts: [],
      VMSSelected:"",
      hostCurrent:{},
      SubnetData: []
    };
    this.handleChange = this.handleChange.bind(this);
    this.CreateSubnet = this.CreateSubnet.bind(this);
    this.DeleteNetwork = this.DeleteNetwork.bind(this);
    this.DeleteSubnet = this.DeleteSubnet.bind(this);
    this.handleVM = this.handleVM.bind(this);
  }


  async GettingData(){
    this.setState({
      status: "loading"
    });
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

    //Getting Data From Network While Mounting
    var NetworksData;
    await GetServiceWithData(BLUEPRINTNET_NETWORK_GET_URL, data).then((res) => {
      NetworksData = JSON.parse(res.data);
      NetworksData.forEach((Network) => {
        Network["subnet"] = [];
      });
      console.log("The Networks Loading", NetworksData);
    });
    //Getting Subnet Details---------------
    var dataGet = {
      project: this.state.project,
      network: "all",
    };

    //Getting Data From Subnet While Mounting
    var SubnetDetails;
    await GetServiceWithData(BLUEPRINTNET_SUBNET_GET_URL, dataGet).then(
      (res) => {
        console.log("data from response of subnet get", res.data);
        SubnetDetails = JSON.parse(res.data);
        //Setting up Network with Subnet
        NetworksData.map((Network, index) => {
          var SubnetofNetwork = [];
          SubnetDetails.map((Subnet) => {
            if (Subnet.nw_name === Network.nw_name) {
              Subnet["host"] = [];
              SubnetofNetwork.push(Subnet);
            }
          });
          Network.subnet = SubnetofNetwork;
        });
        console.log("After Loading Subnet to Network", NetworksData);
      }
    );
      let hostCurrent ={};
    //Getting Data From Host While Mounting
    console.log("data from request to host get", data);
    await GetServiceWithData(BLUEPRINTNET_HOST_GET_URL, data).then((res) => {
      // var datajson = res.data[this.state.nameNetwork][0];
      console.log("data from response of host get", res.data);
      NetworksData.map((Network, index) => {
        if (res.data[Network.nw_name] !== undefined) {
          res.data[Network.nw_name].map((hosts, index) => {
            hosts.map((host, index) => {
              console.log("The host details", host);
              SubnetDetails.map((subnet, index) => {
                console.log("Host details get", host.subnet);
                console.log("Host details get", subnet.cidr);
                if (host.subnet === subnet.cidr) {
                  console.log("Host details going to be pushed", host);
                  hostCurrent["hostname"] = host.host;
                  hostCurrent["type"]= subnet.subnet_type
                  hostCurrent["subnet"]=host.subnet 
                  Network.subnet[index].host.push(host);
                }
              });
            });
          });
        }
        console.log("The Network Having host", Network);
      });
    });
    let VMSDATA;
    //Getting the VMS  Details------------
    await GetServiceWithData(BLUEPRINTNET_GET_VMS, data).then(
      (res)=>{
        VMSDATA = res.data.machine_types;
        console.log("Machine Types",VMSDATA);
      }
    );

    //Setting the State
    this.setState({
      Networks: NetworksData,
      VMS:VMSDATA,
      hostCurrent:hostCurrent,
      status: "loaded"
    });
  }

  async componentDidMount() {
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
    await GetServiceWithData(BLUEPRINTNET_NETWORK_GET_URL, dataGet).then(
      (res) => {
        var NetworksData = JSON.parse(res.data);
        NetworksData.forEach((Network) => {
          Network["subnet"] = [];
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
    //Getting Subnet Details---------------
    var dataGet = {
      project: this.state.project,
      network: NameNetwork,
    };
    await GetServiceWithData(BLUEPRINTNET_SUBNET_GET_URL, dataGet).then(
      (res) => {
        console.log("data from response of subnet get", res.data);
        var NetworksData = this.state.Networks;
        NetworksData[indexNetwork].subnet = JSON.parse(res.data);
        this.setState({
          Networks: NetworksData,
        });
      }
    );
    var dataGet2 = {
      project: this.state.project,
    };

    this.GettingData();
    //Getting the host Details------------
    // await GetServiceWithData(BLUEPRINTNET_HOST_GET_URL, dataGet2).then(
    //   (res) => {
    //     // var datajson = res.data[this.state.nameNetwork][0];
    //     console.log("data from response of host get", res.data);
    //   }
    // );

    //Getting the VMS  Details------------
    // await GetServiceWithData(BLUEPRINTNET_GET_VMS, dataGet2).then(
    //   (res)=>{
    //     var VMSDATA = res.data.machine_types;
    //     console.log("Machine Types",VMSDATA);
    //      this.setState({ VMS:VMSDATA});
    //   }
    // );
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
  async DeleteSubnet(subnetname) {
    console.log("Deleting Subent");
    var data = {
      project: this.state.project,
      subnet_name: subnetname,
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
  handleVM(event) {
    console.log(event.target.value);
    let hostCurrent = this.state.hostCurrent;
    hostCurrent["machine_type"]=event.target.value;
    this.setState({
      hostCurrent,
    })
  }

  //Creating Build-------------------------------------------------------------------------
  async _createBuild() {
    let data = {
      project: this.state.project,
    };
    console.log("Building");
    await PostService(BLUEPRINTNET_BUILD_POST_URL, data).then((res) => {
      console.log("data from response of Build post", res.data);
      var interval = setInterval(this.getStatus, 10000);
      this.setState({ interval: interval});
    });
  }
  getStatus(){
    GetService(BLUEPRINT_STATUS).then((res)=>{
      console.log(res);
    })
  }

  //Creating SaveNetwork-----------------------------------------------------------------
  async _SaveBuild() {
    console.log("Here the data for host Current is saved",this.state.hostCurrent);
    var data={
      project:this.state.project,
      machines:[this.state.hostCurrent]
    }
    console.log(data);
    await PostService(BLUEPRINT_SAVE, data).then((res) => {
      console.log("data from response of Build post", res.data);
    });
  } 

  render() {
    const Networks = this.state.Networks;
    const isLoadingNetwork = Networks.length === 0;
    if (this.state.status === "loading") {
      return (
        <Container>       
         <Loader />
        </Container>

      )
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

            <div className="mt-4 d-flex justify-content-between">
              <Button
                className="media-body py-3 mr-40px text-secondary bg-white"
                variant="light"
                size="lg"
                active
              >
                Cloning <icon.FiCopy />
              </Button>
              <Button
                className="media-body py-3 mr-40px text-secondary bg-white"
                variant="light"
                size="lg"
                active
              >
                Conversion <icon.BsArrowRepeat />
              </Button>
              <Button
                className="media-body py-3 text-secondary bg-white"
                variant="light"
                size="lg"
                active
              >
                Build <icon.BsPlay />
              </Button>
            </div>

            {/* HereTable */}

            <Card className="mt-4 p-2">
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
                          handleVM = {this.handleVM}
                        />
                      ))
                    )}
                  </Table>
                </Container>
              </Card.Body>
            </Card>

            <Row className="m-2">
              <Col>
                <Button
                  variant="success"
                  onClick={this._SaveBuild.bind(this)}
                  size="sm"
                  block
                >
                  Save
                </Button>
              </Col>
              <Col>
                <Button
                  variant="primary"
                  size="sm"
                  onClick={this._createBuild.bind(this)}
                  block
                >
                  Build
                </Button>
              </Col>
              <Col>
                <Button variant="danger" size="sm" block>
                  Reset
                </Button>
              </Col>
            </Row>
          </Container>
        </div>
      );
    }
  }
}
