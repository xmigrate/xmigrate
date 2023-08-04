import React, { Component } from "react";
import {
  Table,
  Button,
  Form,
  Row,
  Col,
} from "react-bootstrap";
import "./NetworkTable.scss";
import * as icon from "react-icons/all";
import { IconContext } from "react-icons";
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
    console.log("The lengeth ",props.Network.subnets.length);
    this.toggleExpander = this.toggleExpander.bind(this);
  }

  toggleExpander(e){
    if (e.target.id === "Del") return;
    if (!this.state.expanded) {
      this.setState({ expanded: true });
    } else {
      this.setState({ expanded: false });
    }
  };



  render() {
    const Subnets = this.props.Network.subnets;
    const isLoadingSubnet = Subnets.length === 0;
    return (
      <tbody className="NetworkTable">
        <tr key={this.props.index} className="NetworkRow tData" onClick={this.toggleExpander}>
          <td >{ this.state.expanded ? <IconContext.Provider value={{ color: "#1DA1F2" }}>
  <div>
  <icon.BsCaretDownFill  /> 
  </div>
</IconContext.Provider> :  <icon.BsCaretRightFill /> } 
           </td>
          <td >{this.props.Network.nw_name}</td>
          {this.props.Provider ==='gcp'?<></>:   <td >{this.props.Network.cidr}</td>}
          <td  onClick={()=>this.props.DeleteNetwork(this.state.Network)}>
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
          <td></td>
        </tr>
        {this.state.expanded && (
          <tr className="expandable tData" key="tr-expander">
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
                      placeholder="Input Subnet CIDR"
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
                        this.props.CreateSubnet(this.props.Network.cidr)
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
                      <th scope="col"></th>
                      <th scope="col"> SUBNET</th>
                      <th scope="col">CIDR</th>
                      <th scope="col">TYPE</th>
                      <th className="col-3"></th>
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
                    this.props.Network.subnets.map((SubnetData, index) => (
                      <SubnetTable
                        key={index}
                        index={index + 1}
                        Subnet={SubnetData}
                        NetworkName={this.state.Network}
                        VMS={this.props.VMS}
                        DeleteSubnet={this.props.DeleteSubnet}
                        handleVM={this.props.handleVM}
                        drag={this.props.drag}
                        dragStart={this.props.dragStart}
                        allowDrop = {this.props.allowDrop}
                        drop = {this.props.drop}
                        BlueprintHostPrepare={this.props.BlueprintHostPrepare}
                        BlueprintHostClone={this.props.BlueprintHostClone}
                        BlueprintHostConvert={this.props.BlueprintHostConvert}
                        BlueprintHostBuild={this.props.BlueprintHostBuild}

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
