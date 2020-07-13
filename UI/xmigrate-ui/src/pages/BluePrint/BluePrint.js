import React, { Component } from 'react'
import './BluePrint.scss'
import { Container, Table, Card, Button, Dropdown, Form, Row, Col } from 'react-bootstrap'
import * as icon from 'react-icons/all'
export default class BluePrint extends Component {

    constructor(props) {
        super(props)
        this.state = {
            hosts: [
                { id: 1, hostname: "Hostname1", ip: "10.170.20.13", subnet: "10.10.0.0/24", network: "10.10.10.0/24", cpu: "inter(R)", core: "1", ram: "10GB", disk: "/dev/xvda" }
            ]
        }
    }

    render() {
        return (
            <div className="BluePrint media-body background-primary">
                <Container className="py-5 ">
                    <h4 className="p-0 m-0">
                        Blueprint
                    </h4>
                    <Card className="mt-4 p-2">
                        <Card.Header className="bg-white">
                            Discovered Hosts
                        </Card.Header>
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
                                    {this.state.hosts.map((data, index) =>
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
                                    )}
                                </tbody>
                            </Table>
                        </Card.Body>
                    </Card>

                    <div className="mt-4 d-flex justify-content-between" >
                        <Button className="media-body py-3 mr-40px text-secondary bg-white" variant="light" size="lg" active>
                            Cloning <icon.FiCopy />
                        </Button>
                        <Button className="media-body py-3 mr-40px text-secondary bg-white" variant="light" size="lg" active>
                            Conversion <icon.BsArrowRepeat />
                        </Button>
                        <Button className="media-body py-3 text-secondary bg-white" variant="light" size="lg" active>
                            Build <icon.BsPlay />
                        </Button>
                    </div>

                    <Card className="mt-4 p-2">
                        <Card.Header className="bg-white d-flex">

                            <Dropdown className="mr-40px media-body">
                                <Dropdown.Toggle variant="outline-dark" >
                                    Dropdown Button
                                    </Dropdown.Toggle>
                                <Dropdown.Menu className="mr-40px">
                                    <Dropdown.Item href="#/action-1">Action</Dropdown.Item>
                                    <Dropdown.Item href="#/action-2">Another action</Dropdown.Item>
                                    <Dropdown.Item href="#/action-3">Something else</Dropdown.Item>
                                </Dropdown.Menu>
                            </Dropdown>

                            <Dropdown className="mr-40px media-body ">
                                <Dropdown.Toggle variant="outline-dark" >
                                    Dropdown Button
                                    </Dropdown.Toggle>
                                <Dropdown.Menu>
                                    <Dropdown.Item href="#/action-1">Action</Dropdown.Item>
                                    <Dropdown.Item href="#/action-2">Another action</Dropdown.Item>
                                    <Dropdown.Item href="#/action-3">Something else</Dropdown.Item>
                                </Dropdown.Menu>
                            </Dropdown>

                            <Dropdown className="mr-40px media-body">
                                <Dropdown.Toggle variant="outline-dark" >
                                    Select Machine Type
                                    </Dropdown.Toggle>
                                <Dropdown.Menu>
                                    <Dropdown.Item href="#/action-1">Action</Dropdown.Item>
                                    <Dropdown.Item href="#/action-2">Another action</Dropdown.Item>
                                    <Dropdown.Item href="#/action-3">Something else</Dropdown.Item>
                                </Dropdown.Menu>
                            </Dropdown>
                            <div className=" d-flex flex-2">
                                <Button className="mr-40px flex-3" variant="success" size="sm">
                                    Create Blueprint
                                </Button>
                                <Button className="flex-3" variant="secondary" >
                                    Start <icon.BsArrowRight />
                                </Button>
                            </div>

                        </Card.Header>

                        <Card.Body>

                            <Container fluid className="blueprint-edit-table">


                                <div className="blueprint-edit-item">
                                    <Row className="font-weight-bold py-3 border-bottom">
                                        <Col xs={{ span: 1 }}>

                                        </Col>
                                        <Col xs={{ span: 2 }}>
                                            NETWORK
                                        </Col>
                                        <Col xs={{ span: 2 }}>
                                            CIDR
                                        </Col>
                                    </Row>

                                    <Row className="border-bottom  py-3">
                                        <Col xs={{ span: 1 }}>
                                            <icon.AiOutlineArrowRight data-toggle="collapse" data-target="#accordion" className="clickable" />
                                        </Col>
                                        <Col xs={{ span: 2 }}>
                                            Network-1
                                            </Col>
                                        <Col xs={{ span: 2 }}>
                                            192.168.0.0/16
                                        </Col>
                                    </Row>
                                    <div id="accordion" className="collapse">
                                        <Row className="font-weight-bold py-3 border-bottom">
                                            <Col xs={{ span: 1 }}>

                                            </Col>
                                            <Col xs={{ span: 2 }}>
                                                SUBNET
                                            </Col>
                                            <Col xs={{ span: 2 }}>
                                                CIDR
                                            </Col>
                                            <Col xs={{ span: 2 }}>
                                                TYPE
                                            </Col>
                                        </Row>
                                        <Row className="border-bottom  py-3">
                                            <Col xs={{ span: 1 }}>
                                                <icon.AiOutlineArrowRight data-toggle="collapse" data-target="#accordion-inner" className="clickable" />
                                            </Col>
                                            <Col xs={{ span: 2 }}>
                                                Subnet-1
                                            </Col>
                                            <Col xs={{ span: 2 }}>
                                                192.168.1.0/24
                                            </Col>
                                            <Col xs={{ span: 2 }}>
                                                <Form>
                                                    <Form.Group controlId="select-type">
                                                        <Form.Control className="select-blueprint-edit" defaultValue="defa" as="select" size="sm" custom>
                                                            <option value="defa" disabled>Select one</option>
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
                                                <Col xs={{ span: 1 }}>

                                                </Col>
                                                <Col xs={{ span: 2 }}>
                                                    HOSTNAME
                                                </Col>
                                                <Col xs={{ span: 2 }}>
                                                    IP
                                                </Col>
                                                <Col xs={{ span: 2 }}>
                                                    MACHINE TYPE
                                                </Col>
                                                <Col xs={{ span: 2 }}>
                                                    IMAGE ID
                                                </Col>
                                                <Col xs={{ span: 2 }}>
                                                    VM ID
                                                </Col>
                                                <Col xs={{ span: 1 }}>
                                                    STATUS
                                                </Col>
                                            </Row>
                                            <Row className=" py-3 ">
                                                <Col xs={{ span: 1 }}>

                                                </Col>
                                                <Col xs={{ span: 2 }}>
                                                    xmigrate
                                                </Col>
                                                <Col xs={{ span: 2 }}>
                                                    192.168.1.5
                                                </Col>
                                                <Col xs={{ span: 2 }}>
                                                    <Form>
                                                        <Form.Group controlId="select-machine-type">
                                                            <Form.Control className="select-blueprint-edit" defaultValue="defa" as="select" size="sm" custom>
                                                                <option value="defa" disabled>Select one</option>
                                                                <option>1</option>
                                                                <option>2</option>
                                                                <option>3</option>
                                                                <option>4</option>
                                                                <option>5</option>
                                                            </Form.Control>
                                                        </Form.Group>
                                                    </Form>
                                                </Col>
                                                <Col xs={{ span: 2 }}>
                                                    xyz
                                                </Col>
                                                <Col xs={{ span: 2 }}>
                                                    abc
                                                </Col>
                                                <Col xs={{ span: 1 }}>
                                                    Processing
                                                </Col>
                                            </Row>
                                        </div>
                                    </div>

                                </div>

                            </Container>
                        </Card.Body>
                    </Card>

                </Container>
            </div>
        )
    }
}



// <Table responsive borderless className="create-layout-table">
//                                 <thead>
//                                     <tr>
//                                         <th>
//                                             {/* # */}
//                                         </th>
//                                         <th>Network</th>
//                                         <th>CIDR</th>
//                                         <th>
//                                             {/* # */}
//                                         </th>

//                                     </tr>
//                                 </thead>
//                                 <tbody >

//                                     <tr data-toggle="collapse" data-target="#accordion" className="clickable">
//                                         <td>
//                                             <icon.AiOutlineArrowRight className="text-dark text-decoration-none" />
//                                         </td>
//                                         <td >
//                                             Network-1
//                                         </td>
//                                         <td>
//                                             192.168.0.0/16
//                                         </td>
//                                         <td>
//                                             {/* # */}
//                                         </td>

//                                     </tr>
//                                     <tr>
//                                         <td colSpan="4">
//                                             <Table responsive borderless id="accordion" className="collapse">
//                                                 <thead>
//                                                     <tr>
//                                                         <th>
//                                                             {/* # */}
//                                                         </th>
//                                                         <th>
//                                                             SUBNET
//                                                         </th>
//                                                         <th>CIDR</th>
//                                                         <th>TYPE</th>
//                                                     </tr>
//                                                 </thead>
//                                                 {/* <tbody>
//                                                     <tr data-toggle="collapse" data-target="#accordion-inner" className="clickable">
//                                                         <td>
//                                                             <icon.AiOutlineArrowRight className="text-dark text-decoration-none" />
//                                                         </td>
//                                                         <td >
//                                                             Subnet-1
//                                                         </td>
//                                                         <td>
//                                                             192.168.1.0/24
//                                                         </td>
//                                                         <td>
//                                                             <Form.Group controlId="exampleForm.ControlSelect1">
//                                                                 <Form.Control as="select">
//                                                                     <option>1</option>
//                                                                     <option>2</option>
//                                                                     <option>3</option>
//                                                                     <option>4</option>
//                                                                     <option>5</option>
//                                                                 </Form.Control>
//                                                             </Form.Group>
//                                                         </td>
//                                                     </tr>
//                                                     <tr id="accordion-inner" className="collapse">
//                                                         <td>
//                                                             inner
//                                                         </td>
//                                                         <td>
//                                                             inner
//                                                         </td>
//                                                         <td>
//                                                             inner
//                                                         </td>
//                                                         <td>
//                                                             inner
//                                                         </td>
//                                                     </tr>
//                                                 </tbody> */}
//                                             </Table>
//                                         </td>
//                                     </tr>

//                                 </tbody>
//                             </Table>