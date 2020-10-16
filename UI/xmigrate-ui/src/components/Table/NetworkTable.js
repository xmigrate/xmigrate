import React, { Component } from "react";
import {
  Container,
  Table,
  Card,
  Button,
  Form,
  Row,
  Col,
} from "react-bootstrap";
import SubnetTable from "./SubnetTable";
export default class NetworkTableRow extends Component {
  constructor(props) {
    super();
    console.log("NetworkRowLoading", props.Network.nw_name);
    this.state = {
      Network: props.Network.nw_name,
      expanded: false,
      Delete: false,
    };
    console.log("The lengeth ",props.Network.subnet.length);
  }

  toggleExpander = (e) => {
    if (e.target.id === "Del") return;
    if (!this.state.expanded) {
      this.setState({ expanded: true });
    } else {
      this.setState({ expanded: false });
    }
  };



  render() {
    const Subnets = this.props.Network.subnet;
    const isLoadingSubnet = Subnets.length === 0;
    return (
      <tbody>
        <tr key={this.props.index} onClick={this.toggleExpander}>
          <td>#{this.props.index}</td>
          <td>{this.props.Network.nw_name}</td>
          <td>{this.props.Network.cidr}</td>
          <td onClick={()=>this.props.DeleteNetwork(this.state.Network)}>
            <svg
              width="1em"
              id="Del"
              height="1em"
              viewBox="0 0 16 16"
              className="bi bi-trash-fill"
              fill="currentColor"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                id="Del"
                fillRule="evenodd"
                d="M2.5 1a1 1 0 0 0-1 1v1a1 1 0 0 0 1 1H3v9a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2V4h.5a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1H10a1 1 0 0 0-1-1H7a1 1 0 0 0-1 1H2.5zm3 4a.5.5 0 0 1 .5.5v7a.5.5 0 0 1-1 0v-7a.5.5 0 0 1 .5-.5zM8 5a.5.5 0 0 1 .5.5v7a.5.5 0 0 1-1 0v-7A.5.5 0 0 1 8 5zm3 .5a.5.5 0 0 0-1 0v7a.5.5 0 0 0 1 0v-7z"
              />
            </svg>
          </td>
        </tr>
        {this.state.expanded && (
          <tr className="expandable" key="tr-expander">
            <td className="uk-background-muted" colSpan={6}>
              <div className="inner">
                <Row className=" py-3">
                  <Col xs={{ span: 2 }}>
                    <Form.Control
                      size="sm"
                      type="text"
                      onChange={this.props.handleChange}
                      placeholder="Subnet Name"
                      name="SubnetName"
                    />
                  </Col>
                  <Col xs={{ span: 2 }}>
                    <Form.Control
                      size="sm"
                      type="text"
                      onChange={this.props.handleChange}
                      placeholder="Inbut Subnet CIDR"
                      name="SubnetCidr"
                    />
                  </Col>
                  <Col xs={{ span: 2 }}>
                    <Form>
                      <Form.Group controlId="select-type">
                        <Form.Control
                          className="select-blueprint-edit"
                          as="select"
                          size="sm"
                          name="Security"
                          custom
                          onChange={this.props.handleChange}
                        >
                          <option value="Public">Public</option>
                          <option value="Private">Private</option>
                        </Form.Control>
                      </Form.Group>
                    </Form>
                  </Col>
                  <Col xs={{ span: 2 }}>
                    <Button
                      className=" media-body"
                      variant="primary"
                      onClick={() =>
                        this.props.CreateSubnet(this.state.Network)
                      }
                      size="sm"
                    >
                      Create
                    </Button>
                  </Col>
                </Row>
                <Table className="bordered hover">
                  <thead>
                    <tr>
                      <th >#</th>
                      <th>SUBNET</th>
                      <th>CIDR</th>
                      <th>TYPE</th>
                      <th></th>
                    </tr>
                  </thead>

                  {isLoadingSubnet ? (
                    <tbody>
                      <tr>
                        <td colSpan={6} className="text-center text-muted">
                          No SubnetData Avaialble...
                        </td>
                      </tr>
                    </tbody>
                  ) : (
                    this.props.Network.subnet.map((SubnetData, index) => (
                      <SubnetTable
                        key={index}
                        index={index + 1}
                        Subnet={SubnetData}
                        VMS={this.props.VMS}
                        DeleteSubnet={this.props.DeleteSubnet}
                        handleVM={this.props.handleVM}
                      />
                    ))
                  )}
                </Table>
              </div>
            </td>
          </tr>
        )}
      </tbody>
    );
  }
}
