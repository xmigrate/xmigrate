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
import GetService ,{ GetServiceWithData} from "../../services/GetService";
import {
  BLUEPRINT_URL,
  BLUEPRINTNET_NETWORK_CREATE_URL,
  BLUEPRINTNET_NETWORK_GET_URL,
} from "../../services/Services";
import PostService from "../../services/PostService";
export default class BluePrint extends Component {
  constructor(props) {
    super(props);
    this.state = {
      cidr: "defa",
      project: "testproject",
      nameNetwork:"",
      hosts: [
        // { id: 1, _id: {$oid:"dummy"},hostname: "Hostname1", ip: "10.170.20.13", subnet: "10.10.0.0/24", network: "10.10.10.0/24", cpu: "inter(R)", core: "1", ram: "10GB", disk: "/dev/xvda" }
      ],
      dataChecking:[],
      blueprintHost: [
        {
          cores: "1",
          cpu_model: "Intel(R) Xeon(R) CPU E5-2676 v3 @ 2.40GHz",
          host: "ip6-localhost",
          ip: "172.31.34.216",
          machine_type: "",
          network: "172.31.32.0/18",
          ports: [
            { type: "tcp", name: "python", port: 22 },
            { type: "tcp", name: "python", port: 22 },
          ],
          project: "testproject",
          public_route: true,
          ram: "1002304 kB",
          status: "Not started",
          subnet: "172.31.34.216/20",
          _id: { $oid: "5f1ae6b29196da32154b53c4" },
        },
        {
          cores: "1",
          cpu_model: "Intel(R) Xeon(R) CPU E5-2676 v3 @ 2.40GHz",
          host: "ip6-localhost",
          ip: "172.31.34.216",
          machine_type: "",
          network: "172.31.32.0/18",
          ports: [
            { type: "tcp", name: "python", port: 22 },
            { type: "tcp", name: "python", port: 22 },
          ],
          project: "testproject",
          public_route: true,
          ram: "1002304 kB",
          status: "Not started",
          subnet: "172.31.34.216/20",
          _id: { $oid: "5f1ae6b29196da32154b53c4" },
        },
      ],
    };
  }

  componentDidMount() {
    GetService(BLUEPRINT_URL).then((res) => {
      console.log(res.data);
      res.data.map((data, index) =>
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

      // Forcefully rerender component
      this.setState({ state: this.state });
    });
  }

  async _createBluePrint() {
    // if (this.state.cidr === "defa") {
    //   alert("Please Select a valid CIDR");
    // } else {
    //   var data = {
    //     cidr: this.state.cidr,
    //     project: this.state.project,
    //   };
    //   PostService(BLUEPRINTNET_NETWORK_CREATE_URL, data).then((res) => {
    //     console.log("data fot as response",res.data);
    //     console.log("data fot as response blueprint",res.data.blueprint);
    //     console.log("data fot as response to json",JSON.parse(res.data.blueprint));
    //     this.state.dataChecking.push(JSON.parse(res.data.blueprint));

    //     this.setState({ state: this.state });
    //   });
    // }

 
     var data = {
        cidr: this.state.cidr,
        project: this.state.project,
        name:this.state.nameNetwork
      };
      console.log(data);
      var dataGet={
        project : this.state.project
      };
      await PostService(BLUEPRINTNET_NETWORK_CREATE_URL, data).then((res) => {
        console.log("data fot as response",res.data);
        // this.setState({ state: this.state });
   
     
   
      });
      await GetServiceWithData(BLUEPRINTNET_NETWORK_GET_URL,dataGet).then((res) => {
        console.log("data fot as response",res.data);
        // this.setState({ state: this.state });
      });

  }
  _setCIDR(e) {
    this.setState({
      cidr: e.target.value,
    });

  
  }
  _setnameNetwork(e) {
    this.setState({
      nameNetwork: e.target.value,
    });
  }
  render() {
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
                  <Form.Control size="md" onChange={this._setCIDR.bind(this)} type="text" placeholder="Input Network CIDR" />
                  </Col>
                  <Col>
                <Form.Control size="md" onChange={this._setnameNetwork.bind(this)} type="text" placeholder="Input Network Name" />
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
                  {/* <Form.Control
                    className=""
                    defaultValue="defa"
                    as="select"
                    onChange={this._setCIDR.bind(this)}
                    custom
                  >
                    <option value="defa" disabled>
                      Select VPC CIDR
                    </option>
                    <option value="172.16.0.0">172.16.0.0</option>
                    <option value="10.0.0.0">10.0.0.0</option>
                  </Form.Control> */}
                  </Row>
             
                </Form.Group>
              </Form>

         
             
            </Card.Header>

            <Card.Body>
              <Container fluid className="blueprint-edit-table">
                <div className="blueprint-edit-item">
                  <Row className="font-weight-bold py-3 border-bottom">
                    <Col xs={{ span: 1 }}></Col>
                    <Col xs={{ span: 2 }}>NETWORK</Col>
                    <Col xs={{ span: 2 }}>CIDR</Col>
                  </Row>

                  {this.state.dataChecking.map((data, index) => (
                    <div>
                      <Row className="border-bottom  py-3">
                        <Col xs={{ span: 1 }}>
                          <icon.AiOutlineArrowRight
                            data-toggle="collapse"
                            data-target="#accordion"
                            className="clickable"
                          />
                        </Col>
                        <Col xs={{ span: 2 }}>Network-1</Col>
                        <Col xs={{ span: 2 }}>{data[index].ip}</Col>
                      </Row>
                      <div id="accordion" className="collapse">
                        <Row className="font-weight-bold py-3 border-bottom">
                          <Col xs={{ span: 1 }}></Col>
                          <Col xs={{ span: 2 }}>SUBNET</Col>
                          <Col xs={{ span: 2 }}>CIDR</Col>
                          <Col xs={{ span: 2 }}>TYPE</Col>
                        </Row>
                        <Row className="border-bottom  py-3">
                          <Col xs={{ span: 1 }}>
                            <icon.AiOutlineArrowRight
                              data-toggle="collapse"
                              data-target="#accordion-inner"
                              className="clickable"
                            />
                          </Col>
                          <Col xs={{ span: 2 }}>Subnet-1</Col>
                          <Col xs={{ span: 2 }}>{data[index].subnet}</Col>
                          <Col xs={{ span: 2 }}>
                            <Form>
                              <Form.Group controlId="select-type">
                                <Form.Control
                                  className="select-blueprint-edit"
                                  defaultValue="defa"
                                  as="select"
                                  size="sm"
                                  custom
                                >
                                  <option value="defa" disabled>
                                    Select one
                                  </option>
                                  <option>1</option>
                                  <option>2</option>
                                  <option>3</option>
                                  <option>4</option>
                                  <option>5</option>
                                </Form.Control>
                              </Form.Group>
                            </Form>
                          </Col>
                        </Row>
                        <div id="accordion-inner" className="collapse">
                          <Row className="font-weight-bold py-3 ">
                            <Col xs={{ span: 1 }}></Col>
                            <Col xs={{ span: 2 }}>HOSTNAME</Col>
                            <Col xs={{ span: 2 }}>IP</Col>
                            <Col xs={{ span: 2 }}>MACHINE TYPE</Col>
                            <Col xs={{ span: 2 }}>IMAGE ID</Col>
                            <Col xs={{ span: 2 }}>VM ID</Col>
                            <Col xs={{ span: 1 }}>STATUS</Col>
                          </Row>
                          <Row className=" py-3 ">
                            <Col xs={{ span: 1 }}></Col>
                            <Col xs={{ span: 2 }}>xmigrate</Col>
                            <Col xs={{ span: 2 }}>192.168.1.5</Col>
                            <Col xs={{ span: 2 }}>
                              <Form>
                                <Form.Group controlId="select-machine-type">
                                  <Form.Control
                                    className="select-blueprint-edit"
                                    defaultValue="defa"
                                    as="select"
                                    size="sm"
                                    custom
                                  >
                                    <option value="defa" disabled>
                                      Select one
                                    </option>
                                    <option>Pul</option>
                                    <option></option>bic
                                  </Form.Control>
                                </Form.Group>
                              </Form>
                            </Col>
                            <Col xs={{ span: 2 }}>xyz</Col>
                            <Col xs={{ span: 2 }}>abc</Col>
                            <Col xs={{ span: 1 }}>Processing</Col>
                          </Row>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </Container>
            </Card.Body>
          </Card> 


        </Container>
      </div>
    );
  }
}
