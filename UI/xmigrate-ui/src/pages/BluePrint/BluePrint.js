import React, { Component } from 'react'
import './BluePrint.scss'
import { Container, Table, Card, Button, Dropdown } from 'react-bootstrap'
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

                </Container>
            </div>
        )
    }
}
