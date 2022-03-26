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
  Modal,
  Toast,
  Spinner
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
  BLUEPRINT_UDATE_HOST,
  BLUEPRINT_NETWORK_BUILD,
  BLUEPRINT_HOST_BUILD,
  BLUEPRINT_HOST_CONVERT,
  BLUEPRINT_HOST_CLONE
} from "../../services/Services";
import PostService from "../../services/PostService";
import Loader from "../../components/Loader/Loader";
import NetworkTableRow from "../../components/Table/NetworkTable";
import HostTable from "../../components/Table/HostTable";
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
      provider: props.CurrentPro.provider,
      status: "loading",
      VMS: [],
      hosts: [],
      VMSSelected: "",
      hostCurrent: {},
      SubnetData: [],
      BuildStatus: false,
      ShowAlertReset: false,
      ShowAlertBuild: false,
      ShowAlertSave: false,
      showUpdateAlert: false,
      showUpdateMessage: "",
      expandedHost: false,
      BuildNetworkBtnDis: false,
      hostAlert: "Alert",
      buttonStatus: ""
    };
    this.handleChange = this.handleChange.bind(this);
    this.CreateSubnet = this.CreateSubnet.bind(this);
    this.DeleteNetwork = this.DeleteNetwork.bind(this);
    this.DeleteSubnet = this.DeleteSubnet.bind(this);
    this.handleVM = this.handleVM.bind(this);
    this.drag = this.drag.bind(this);
    this.allowDrop = this.allowDrop.bind(this);
    this.drop = this.drop.bind(this);
    this.getStatus = this.getStatus.bind(this);
    this._BlueprintHostClone = this._BlueprintHostClone.bind(this);
    this._BlueprintHostConvert = this._BlueprintHostConvert.bind(this);
    this._BlueprintHostBuild = this._BlueprintHostBuild.bind(this);
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
    let status;
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

      NetworksDatas.forEach((Network, index) => {
        Network.subnets.forEach((subnet, index) => {
          subnet.hosts.forEach((host, index) => {
            status = parseInt(host["status"]);
            if ((status > -25 && status <= -20) || status === 20) {
              host["BtStatus"] = "clone";
              host["BtProgress"] = "cloneCompleted";
            } else if ((status <= -25 && status > -35) || status === 25) {
              host["BtStatus"] = "convert";
              host["BtProgress"] = "convertCompleted";
            } else if ((status <= -35 && status > -100 ) ||status === 35){
              host["BtStatus"] = "build";
              host["BtProgress"] = "buildCompleted";
            }
            else if(status === 0){
              host["BtStatus"] = "BuildNetwork";
            }

            if(status >20 && status <25 ){
              host["BtProgress"] = "cloneStarted";
            }
            else if(status >25 && status <35){
              host["BtProgress"] = "convertStarted";
            }else if(status >25 && status >100 ){
              host["BtProgress"] = "buildStarted";
            }
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
    console.log("Network Data:", NetworksDatas);
    console.log("Status:", status);
    let BuildNetworkBtnDisflag = false;
    if (status >= 20) {
      BuildNetworkBtnDisflag = true;
    }
    let btStatus;
    if(status <20 && status >0){
      btStatus = "BuildProgress"
      BuildNetworkBtnDisflag = true;
    }
    //Setting the State
    this.setState({
      Networks: NetworksDatas,
      VMS: VMSDATA,
      hostCurrents: hostCurrents,
      status: "loaded",
      BuildNetworkBtnDis: BuildNetworkBtnDisflag,
      buttonStatus :btStatus
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
          disk: data.disk_details
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
    NetworksData.forEach((Network, index) => {
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
    hostCurrent.forEach((hostCur, index) => {
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
    this.handleAlertCloseBuild();
    let data = {
      project: this.state.project,
    };
    this.setState({ BuildStatus: true })
    console.log("Building");
    await PostService(BLUEPRINTNET_BUILD_POST_URL, data).then((res) => {
      console.log("data from response of Build post", res.data);
      var interval = setInterval(this.getStatus, 3000);
      this.setState({ interval: interval });
    });
  }


  //OLd Getting Status Migration------------------------------------------------
  // getStatus() {
  //   let data1 = {
  //     project: this.state.project,
  //   };
  //   GetServiceWithData(BLUEPRINT_STATUS, data1).then((res) => {
  //     console.log("Response For Status", res);
  //     let flag;
  //     let NetworksData = this.state.Networks;
  //     //Setting the host status
  //     NetworksData.forEach((Network, index) => {
  //       Network.subnets.forEach((subnet, index) => {
  //         subnet.hosts.forEach((host, index) => {
  //           res.data.forEach((hostRes, index) => {
  //             if (host.host === hostRes.host) {
  //               host["status"] = hostRes.status;
  //               if (parseInt(hostRes.status) < 100) {
  //                 flag = false;
  //               }
  //               else {
  //                 flag = true;
  //               }
  //             }
  //           });
  //         });
  //       });
  //     });
  //     if (flag) {
  //       clearInterval(this.state.intervalId);

  //       this.setState({ BuildStatus: false, showUpdateAlert: true, showUpdateMessage: "Build Successfull!!" })
  //     }
  //     this.setState({
  //       Networks: NetworksData,
  //     });
  //   });
  // }



  //Creating SaveNetwork-----------------------------------------------------------------
  async _SaveBuild() {
    console.log(
      "Here the data for host Current is saved",
      this.state.hostCurrents
    );
    let hostData = this.state.hostCurrents
    hostData.forEach((host, index) => {
      if (host.type === "Public" || host.type === "True") {
        host["type"] = "True"
      }
      else {
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
      this.setState({ showUpdateAlert: true, showUpdateMessage: "Save Blueprint Successfull.", ShowAlertSave: false, hostAlert: "Alert" })
    });
  }

  //--------------Reset the Network Table
  async _Reset() {
    // this.handleAlertCloseReset();
    console.log("Reseting....");
    var NetworksData = this.state.Networks;
    NetworksData.forEach((Network, index) => {
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
    this.setState({ showUpdateAlert: true, showUpdateMessage: "Reset Successfull.", BuildNetworkBtnDis: false, hostAlert: "Alert", ShowAlertReset: false })

  }

  // Draging and Drop Functionality
  drag(ev, host, index, subnetname, nw_name) {
    let data = {
      host: host,
      index: index,
      ChangeSubnet: subnetname,
      ChangeNetwork: nw_name,
    };
    console.log("On drag", data);
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
    if (nw_name === data.ChangeNetwork && subnetname === data.ChangeSubnet) {
      console.log("Same Place");
      SamePlace = true;
    }
    if (SamePlace === false) {
      console.log("On Drop",);
      console.log(subnetname);
      console.log(nw_name);
      var NetworksData = this.state.Networks;
      NetworksData.forEach((Network, index) => {
        if (Network.nw_name === data.ChangeNetwork) {
          Network.subnets.forEach((subnet, index) => {
            if (subnet.name === data.ChangeSubnet) {
              subnet.hosts.splice(data.index, 1);
            }
          });
          if (Network.nw_name === nw_name) {
            Network.subnets.forEach((subnet, index) => {
              if (subnet.name === subnetname) {
                data.host["subnet"] = subnet.cidr;
                subnet.hosts.push(data.host);
              }
            });
          }

        } else if (Network.nw_name === nw_name) {
          Network.subnets.forEach((subnet, index) => {
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
        machines: [data.host]
      }
      console.log("data passinf to the url", data1);
      PostService(BLUEPRINT_UDATE_HOST, data1).then((res) => {
        console.log("After Drag and drop", res.data);
      });
      this.setState({
        Networks: NetworksData,
      });
      this.GettingData();
    }

  }


  //BluePrintNetworkBuild-------------------------------------------------------------------------
  async _BlueprintNetworkBuild() {
    console.log("Network Build");
    var data = {
      project: this.state.project,
    };
    console.log("Sending", data);
    await PostService(BLUEPRINT_NETWORK_BUILD, data).then((res) => {
      console.log("data from response of Network Build post", res.data);
      var interval = setInterval(this.getStatus, 60000);
      this.setState({ intervalId: interval, ShowAlertBuild: false, BuildNetworkBtnDis: true, buttonStatus: "BuildProgress" });
      //Check status and Status should be 60
    });

  }

  //BlueprintHostClone-------------------------------------------------------------------------
  async _BlueprintHostClone(hostName) {
    console.log("Network Clone", hostName);
    var data = {
      project: this.state.project,
      hostname: hostName,
    };
    console.log(data);
    //Updating progress to load spinner
    let NetworksData = this.state.Networks;
    NetworksData.forEach((Network, index) => {
      Network.subnets.forEach((subnet, index) => {
        subnet.hosts.forEach((host, index) => {
          if(host.host === hostName){
            host["BtProgress"] = "cloneStarted";
          }
        })
      })
      })
    await PostService(BLUEPRINT_HOST_CLONE, data).then((res) => {
      console.log("data from response of  Clone post", res.data);
      var interval = setInterval(this.getStatus, 60000);
      this.setState({ intervalId: interval ,Networks:NetworksData});
    });
  }

  //BlueprintHostConvert-------------------------------------------------------------------------
  async _BlueprintHostConvert(hostName) {
    console.log("Network Convert", hostName);
    var data = {
      project: this.state.project,
      hostname: hostName,
    };
     //Updating progress to load spinner
     let NetworksData = this.state.Networks;
     NetworksData.forEach((Network, index) => {
       Network.subnets.forEach((subnet, index) => {
         subnet.hosts.forEach((host, index) => {
           if(host.host === hostName){
             host["BtProgress"] = "convertStarted";
           }
         })
       })
       })
    console.log("Networks Data",NetworksData);
    console.log("Hostname",hostName);
    await PostService(BLUEPRINT_HOST_CONVERT, data).then((res) => {
      console.log("data from response of Network Convert post", res.data);
      var interval = setInterval(this.getStatus, 60000);
      this.setState({ intervalId: interval ,Networks:NetworksData});
    });
  }

  //BlueprintHostBuild-------------------------------------------------------------------------
  async _BlueprintHostBuild(hostName) {
    console.log("Network Build", hostName);
    var data = {
      project: this.state.project,
      hostname: hostName,
    };
      //Updating progress to load spinner
      let NetworksData = this.state.Networks;
      NetworksData.forEach((Network, index) => {
        Network.subnets.forEach((subnet, index) => {
          subnet.hosts.forEach((host, index) => {
            if(host.host === hostName){
              host["BtProgress"] = "buildStarted";
            }
          })
        })
        })
    console.log(data);
    await PostService(BLUEPRINT_HOST_BUILD, data).then((res) => {
      console.log("data from response of  Build post", res.data);
      var interval = setInterval(this.getStatus, 60000);
      this.setState({ intervalId: interval ,Networks:NetworksData});
    });
  }

  // Getting Status Migration------------------------------------------------
  getStatus() {
    let UpdateMessage;
    let hostAlert;
    let data1 = {
      project: this.state.project,
    };
    GetServiceWithData(BLUEPRINT_STATUS, data1).then((res) => {
      console.log("Response For Status", res);
      let flag = false;
      let NetworksData = this.state.Networks;
      //Setting the host status
      NetworksData.forEach((Network, index) => {
        Network.subnets.forEach((subnet, index) => {
          subnet.hosts.forEach((host, index) => {
            res.data.forEach((hostRes, index) => {
              if (host.host === hostRes.host) {
                console.log(hostRes.status);
                host["status"] = hostRes.status;
                // host["BtStatus"] = hostRes.status;
                console.log("Status of Button", host["BtStatus"]);
                if ((parseInt(hostRes.status) < 20 && host["BtStatus"] === "BuildNetwork") || (parseInt(hostRes.status) < 25 && host["BtStatus"] === "clone") || (parseInt(hostRes.status) < 35 && host["BtStatus"] === "convert") || (parseInt(hostRes.status) < 100 && host["BtStatus"] === "build")) {
                  flag = false;
                }
                else {
                  flag = true;
                  if (host["BtStatus"] === "BuildNetwork") {
                    hostAlert = host.host;
                    UpdateMessage = "Build Network Successfull!!";
                    host["BtStatus"] = "clone"
                    console.log(host["BtStatus"]);
                  }
                  else if (host["BtStatus"] === "clone") {
                    hostAlert = host.host;
                    UpdateMessage = "Clone Completed Successfull!!";
                    host["BtProgress"] = "cloneCompleted";
                    host["BtStatus"] = "convert";
                  }
                  else if (host["BtStatus"] === "convert") {
                    hostAlert = host.host;
                    UpdateMessage = "Convert Completed Successfull!!";
                    host["BtProgress"] = "convertCompleted";
                    host["BtStatus"] = "build";
                  }
                  else if (host["BtStatus"] === "build") {
                    hostAlert = host.host;
                    UpdateMessage = "Build Completed Successfull!!";
                    host["BtProgress"] = "buildCompleted";
                    host["BtStatus"] = "BuildNetwork";
                  }
                }
              }
            });
          });
        });
      });
      if (flag) {

        clearInterval(this.state.intervalId);
        this.setState({ Networks: NetworksData,BuildStatus: false, showUpdateAlert: true, showUpdateMessage: UpdateMessage, hostAlert: hostAlert, buttonStatus: "BuildCompleted" })
      }
      else{
      this.setState({
        Networks: NetworksData,
      });
    }
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
      );
    } else {
      return (
        <div className="BluePrint media-body background-primary">

          {/* <Alert id="message" className="m-2" show={this.state.showUpdateAlert} variant="primary" onClose={() => this.setState({ showUpdateAlert: false })} dismissible>
              <p>{this.state.showUpdateMessage}</p>
            </Alert>  */}

          <Toast id="message" show={this.state.showUpdateAlert} onClose={() => this.setState({ showUpdateAlert: false })}>
            <Toast.Header>
              <strong className="me-auto">{this.state.hostAlert}</strong>
            </Toast.Header>
            <Toast.Body>{this.state.showUpdateMessage}</Toast.Body>
          </Toast>

          <Container className="py-4 ">
            <h4 className="p-0 m-0 HeadingPage">Blueprint</h4>

            <Card className="mt-4 p-2">
              <Card.Header className="bg-white">Discovered Hosts</Card.Header>
              <Card.Body>
                <Table responsive borderless>
                  <thead>
                    <tr className="tName">
                      <th></th>
                      <th>Hostname</th>
                      <th>IP</th>
                      <th>Subnet</th>
                      <th>Network</th>
                      <th>CPU Model</th>
                      <th>Core</th>
                      <th>Ram</th>
                    </tr>
                  </thead>
                  {this.state.hosts.map((data, index) => (
                    <HostTable key={index} index={index} data={data} />
                  ))}

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
                      {this.state.provider === 'gcp' ? <></> :
                        <Col>
                          <Form.Control
                            size="md"
                            onChange={this.handleChange}
                            type="text"
                            placeholder="Input Network CIDR"
                            name="NetworkCIDR"
                          />
                        </Col>
                      }
                      <Col>
                        <Button
                          className=" media-body successGreen"
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
                  <Table className=" hover">
                    <thead className="tName">
                      <tr>
                        <th scope="col"></th>
                        <th scope="col">NETWORK</th>
                        {this.state.provider === 'gcp' ? <></> : <th scope="col">CIDR</th>}
                        <th scope="col"></th>
                        <th className="col-5"></th>
                      </tr>
                    </thead>

                    {isLoadingNetwork ? (
                      <tbody>
                        <tr className="tData">
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
                          Provider={this.state.provider}
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
                          BlueprintHostClone={this._BlueprintHostClone}
                          BlueprintHostConvert={this._BlueprintHostConvert}
                          BlueprintHostBuild={this._BlueprintHostBuild}

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
                className="media-body py-3 mr-40px text-success bt-main btn-Blueprint"
                // onClick={this._SaveBuild.bind(this)}
                // onClick={this.handleAlertOpenSave.bind(this)}
                onClick={() => this.setState({ ShowAlertSave: true })}
                disabled={this.state.BuildStatus}
                size="lg"
              >
                Save <icon.FiCopy />
              </Button>
              <Button
                variant="primary"
                className="media-body py-3 mr-40px text-primary  bt-main btn-Blueprint"
                // onClick={this._createBuild.bind(this)}
                onClick={() => this.setState({ ShowAlertBuild: true })}
                disabled={this.state.BuildStatus || this.state.BuildNetworkBtnDis}
                size="lg"
              >{
                  this.state.buttonStatus === "BuildProgress" ? <><Spinner as="span" animation="grow" size="sm" role="status"  aria-hidden="true"/> In Progess...</> : <>Build Network <icon.BsPlay /></>

                }
              </Button>
              <Button
                variant="danger"
                className="media-body py-3 text-danger  bt-main btn-Blueprint"
                // onClick={this._Reset.bind(this)}
                onClick={() => this.setState({ ShowAlertReset: true })}
                disabled={this.state.BuildStatus}
                size="lg"
              >
                Reset <icon.BsArrowRepeat />
              </Button>
            </div>
          </Container>


          {/* Reset Alert */}

          <Modal show={this.state.ShowAlertReset}
            onHide={() => this.setState({ ShowAlertReset: false })}
          >
            <Modal.Header closeButton>
              <Modal.Title>Reset Project</Modal.Title>
            </Modal.Header>
            <Modal.Body>Do you want to Reset?</Modal.Body>
            <Modal.Footer>
              <Button variant="secondary"
                onClick={() => this.setState({ ShowAlertReset: false })}
              >
                Close
              </Button>
              <Button variant="primary"
                onClick={this._Reset.bind(this)}
              >
                Reset
              </Button>
            </Modal.Footer>
          </Modal>



          {/* Build Alert */}

          <Modal show={this.state.ShowAlertBuild}
            onHide={() => this.setState({ ShowAlertBuild: false })}
          >
            <Modal.Header closeButton>
              <Modal.Title>Build Project</Modal.Title>
            </Modal.Header>
            <Modal.Body>Do you want to Build?</Modal.Body>
            <Modal.Footer>
              <Button variant="secondary"
                onClick={() => this.setState({ ShowAlertBuild: false })}
              >
                Close
              </Button>
              <Button variant="primary"
                // onClick={this._createBuild.bind(this)}
                onClick={this._BlueprintNetworkBuild.bind(this)}
              >
                Build
              </Button>
            </Modal.Footer>
          </Modal>



          {/* Save Alert */}
          <Modal show={this.state.ShowAlertSave}
            onHide={() => this.setState({ ShowAlertSave: false })}
          >
            <Modal.Header closeButton>
              <Modal.Title>Save BluePrint</Modal.Title>
            </Modal.Header>
            <Modal.Body>Do you want to Save?</Modal.Body>
            <Modal.Footer>
              <Button variant="secondary"
                // onClick={this.handleAlertCloseSave.bind(this)}
                onClick={() => this.setState({ ShowAlertSave: false })}
              >
                Close
              </Button>
              <Button variant="primary"
                onClick={this._SaveBuild.bind(this)}
              >
                Save
              </Button>
            </Modal.Footer>
          </Modal>
        </div>
      );
    }
  }
}
