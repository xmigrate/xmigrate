import React, { Component } from "react";
import "./Settings.scss";
import {
  Container,
  Card,
  Button,
  Form,
  Row,
  Col,
  Alert
} from "react-bootstrap";
import { FaAngleRight, FaAws, FaCloud } from "react-icons/fa";
import { SiMicrosoftazure, SiGooglecloud } from "react-icons/si";
import {
  BLUEPRINT_GET_STORAGE,
  BLUEPRINT_UPDATE_STORAGE
} from "../../services/Services";
import { GetServiceWithData } from "../../services/GetService";
import PostService from "../../services/PostService";
export default class Settings extends Component {
  constructor(props) {
    super();
    console.log("The props Received:", props.CurrentPro);
    let input = {};
    input["name"] = props.CurrentPro.name;
    input["subscription_id"] = props.CurrentPro.subscription_id;
    input["provider"] = props.CurrentPro.provider;
    input["resource_group"] = props.CurrentPro.resource_group;
    input["secret"] = props.CurrentPro.secret;
    input["tenant_id"] = props.CurrentPro.tenant_id;
    input["location"] = props.CurrentPro.location;
    input["client_id"] = props.CurrentPro.client_id;
    input["storage"] = "";
    input["container"] = "";
    input["secret_key_aws"] = props.CurrentPro.secret_key;
    input["access_key_aws"] = props.CurrentPro.access_key;
    this.state = {
      project: props.CurrentPro.name,
      input: input,
      status: "Verify",
      errors: {},
      locations: [],
      showUpdateAlert:false
    };
    this.handleChange = this.handleChange.bind(this);
    this.handleProvider = this.handleProvider.bind(this);
    this.handleStorageUpdate = this.handleStorageUpdate.bind(this);

  }

  // Some statements are commented in this project for updating future provision of Project Settings
  async componentDidMount() {
    var data = {
      project: this.state.project,
      provider: this.state.input.provider
    };
    let input = this.state.input;
    await GetServiceWithData(BLUEPRINT_GET_STORAGE, data).then((res) => {
      let data = JSON.parse(res.data);
      console.log("Printing Getting Data", data);
      if (data.length !== 0) {
        input["storage"] = data[0].storage;
        input["container"] = data[0].container;
        input["access_key_azure"] = data[0].access_key;
        input["bucket"] = data[0].bucket;
        input["secret_key_aws_storage"] = data[0].secret_key
        input["access_key_aws_storage"] = data[0].access_key;
      }
    })
    this.setState({
      input,
    });
  }

  handleChange(event) {
    let input = this.state.input;
    input[event.target.name] = event.target.value;
    this.setState({
      input,
    });
  }
  handleProvider(text) {
    let input = this.state.input;
    input["provider"] = text;
    console.log(this.state);
    this.setState({
      input,
    });
  }


  async handleStorageUpdate(event) {
    event.preventDefault();
    if (this.state.input.provider === "aws") {
      var data = {
        provider: this.state.input.provider,
        project: this.state.input.name,
        bucket: this.state.input.bucket,
        access_key: this.state.input.access_key_aws_storage,
        secret_key: this.state.input.secret_key_aws_storage
      }
    } else {
      var data = {
        provider: this.state.input.provider,
        project: this.state.input.name,
        storage: this.state.input.storage,
        container: this.state.input.container,
        access_key: this.state.input.access_key_azure
      }
    }
    console.log(data);
    await PostService(BLUEPRINT_UPDATE_STORAGE, data).then((res) => {
      console.log(res);
      this.setState({
        showUpdateAlert:true
      })
    })

  }

  validate() {
    let input = this.state.input;
    let errors = {};
    let isValid = true;
    return isValid;
  }

  closeAlertUpdate(){
    this.setState({
      showUpdateAlert:false
    })
  }

  render() {
    return (
      
      <div className=" Settings media-body background-primary ">
   
        <Container className="py-5 ">
        <Alert className="m-2" show={this.state.showUpdateAlert} variant="primary" onClose={this.closeAlertUpdate.bind(this)} dismissible>
        <p>Updated!!</p>
      </Alert>
          <h4 className="p-0 m-0">Project Settings</h4>
          <Row className="py-5 ">
            <Col md="6" className="bg-white shadow-sm rounded ">
              <div className="p-3 d-flex flex-column justify-content-between h-100">
                <Form className="FormStyle" >
                  <Form.Group className="register bg-blue">
                    <Form.Label>Project Name</Form.Label>
                    <Form.Control
                      type="text"
                      id="ProjectName"
                      onChange={this.handleChange}
                      aria-describedby="ProjectHelp"
                      placeholder="Project Name"
                      disabled={true}
                      value={this.state.input.name}
                      name="name"
                    />
                  </Form.Group>
                  <Form.Group>
                    <Form.Label>Select Provider</Form.Label>
                  </Form.Group>
                  <Row className="Providerrow">
                    <Col
                      className={
                        "ProviderCol" +
                        (this.state.input.provider === "aws" ? " active" : "")
                      }
                    >
                      <Card>
                        <Card.Body
                          className="Provider"
                        // onClick={() => this.handleProvider("aws")}
                        >
                          <FaAws size={50} />
                        </Card.Body>
                      </Card>
                    </Col>
                    <Col
                      className={
                        "ProviderCol" +
                        (this.state.input.provider === "azure" ? " active" : "")
                      }
                    >
                      <Card>
                        <Card.Body
                          className="Provider"
                        // onClick={() => this.handleProvider("azure")}
                        >
                          <SiMicrosoftazure size={50} />
                        </Card.Body>
                      </Card>
                    </Col>
                    {/* <Col className={"ProviderCol"+ (this.state.input.provider == "GoogleCloud" ? ' active' : '')}>
                        <Card>
                          <Card.Body className="Provider" onClick={()=>this.handleProvider("GoogleCloud")}>
                            <SiGooglecloud size={50} />
                          </Card.Body>
                        </Card>
                      </Col> */}
                  </Row>

                  <Form.Group
                    className="register bg-blue"
                    style={{
                      display:
                        this.state.input.provider === "azure"
                          ? " block"
                          : "none",
                    }}
                  >
                    <Form.Label>Subscription</Form.Label>
                    <Form.Control
                      type="text"
                      onChange={this.handleChange}
                      placeholder="Subscription id"
                      disabled={true}
                      value={this.state.input.subscription_id}
                      name="subscription_id"
                    />
                  </Form.Group>
                  <Form.Group
                    className="register bg-blue"
                    style={{
                      display:
                        this.state.input.provider === "azure"
                          ? " block"
                          : "none",
                    }}
                  >
                    <Form.Label>Client Id</Form.Label>
                    <Form.Control
                      type="text"
                      onChange={this.handleChange}
                      placeholder="Client id"
                      disabled={true}
                      name="client_id"
                      value={this.state.input.client_id}
                    />
                  </Form.Group>

                  <Form.Group
                    className="register bg-blue"
                    style={{
                      display:
                        this.state.input.provider === "azure"
                          ? " block"
                          : "none",
                    }}
                  >
                    <Form.Label>Secret Key</Form.Label>
                    <Form.Control
                      type="text"
                      onChange={this.handleChange}
                      placeholder="secret_key"
                      disabled={true}
                      value={this.state.input.secret}
                      name="secret"
                    />
                  </Form.Group>
                  <Form.Group
                    className="register bg-blue"
                    style={{
                      display:
                        this.state.input.provider === "aws" ? " block" : "none",
                    }}
                  >
                    <Form.Label>Secret Key</Form.Label>
                    <Form.Control
                      type="text"
                      onChange={this.handleChange}
                      placeholder="Secret key"
                      disabled={true}
                      value={this.state.input.secret_key_aws}
                      name="secret_key"
                    />
                  </Form.Group>
                  <Form.Group
                    className="register bg-blue"
                    style={{
                      display:
                        this.state.input.provider === "aws" ? " block" : "none",
                    }}
                  >
                    <Form.Label>Access Key</Form.Label>
                    <Form.Control
                      type="text"
                      onChange={this.handleChange}
                      placeholder="Access key"
                      disabled={true}
                      value={this.state.input.access_key_aws}
                      name="access_key"
                    />
                  </Form.Group>
                  <Form.Group
                    className="register bg-blue"
                    style={{
                      display:
                        this.state.input.provider === "azure"
                          ? " block"
                          : "none",
                    }}
                  >
                    <Form.Label>Tenat Id</Form.Label>
                    <Form.Control
                      type="text"
                      onChange={this.handleChange}
                      placeholder="Tenant Id"
                      disabled={true}
                      value={this.state.input.tenant_id}
                      name="tenant_id"
                    />
                  </Form.Group>
                  <Form.Group
                    className="register bg-blue"
                    style={{
                      display:
                        this.state.input.provider === "azure" &&
                          this.state.status === "Create Project"
                          ? " block"
                          : "none",
                    }}
                  >
                    <Form.Label>Resource Group</Form.Label>
                    <Form.Control
                      type="text"
                      onChange={this.handleChange}
                      placeholder="Resource Group"
                      disabled={true}
                      name="resource_group"
                    />
                  </Form.Group>
                  <Form.Group
                    className="register bg-blue"
                  >
                    <Form.Label>Select Location</Form.Label>
                    <Form.Control
                      as="select"
                      name="location"
                      onChange={this.handleChange}
                      disabled={true}
                      defaultValue={this.state.input.location}
                    >
                      <option>{this.state.input.location}</option>
                      {this.state.locations.map((location) => (
                        <option key={location} value={location}>
                          {location}
                        </option>
                      ))}
                    </Form.Control>
                  </Form.Group>

                  {/* <Button
                    type="submit"
                    className="btn btn-primary
                       col-lg-12"
                  >
                    Update
                    <FaAngleRight size={20} />
                  </Button> */}
                </Form>
              </div>
            </Col>


            {/* Storage Details */}
            <Col
              md={{ span: 5, offset: 1 }}
              className="bg-white shadow-sm rounded "
            >
              <div className="p-3 d-flex flex-column justify-content-between">
                <h4>Storage</h4>
                <Form className="FormStyle" onSubmit={this.handleStorageUpdate}>

                  {/* AZURE */}
                  <Form.Group className="register bg-blue"
                    style={{
                      display:
                        this.state.input.provider === "azure" ? " block" : "none",
                    }}>
                    <Form.Label>Storage</Form.Label>
                    <Form.Control
                      type="text"
                      onChange={this.handleChange}
                      placeholder="Storage"
                      value={this.state.input.storage}
                      name="storage"
                    />
                  </Form.Group>
                  <Form.Group className="register bg-blue"
                    style={{
                      display:
                        this.state.input.provider === "azure" ? " block" : "none",
                    }}
                  >
                    <Form.Label>Container</Form.Label>
                    <Form.Control
                      type="text"
                      onChange={this.handleChange}
                      placeholder="Container"
                      value={this.state.input.container}
                      name="container"
                    />
                  </Form.Group>


                  <Form.Group className="register bg-blue" style={{
                    display:
                      this.state.input.provider === "azure" ? " block" : "none",
                  }}>
                    <Form.Label>Access Key</Form.Label>
                    <Form.Control
                      type="text"
                      onChange={this.handleChange}
                      placeholder="Access key"
                      value={this.state.input.access_key_azure}
                      name="access_key"
                    />
                  </Form.Group>

                  {/* AWS */}

                  <Form.Group className="register bg-blue" style={{
                    display:
                      this.state.input.provider === "aws" ? " block" : "none",
                  }}>
                    <Form.Label>Bucket</Form.Label>
                    <Form.Control
                      type="text"
                      onChange={this.handleChange}
                      placeholder="bucket"
                      value={this.state.input.bucket}
                      name="bucket"
                    />
                  </Form.Group>
                  <Form.Group className="register bg-blue" style={{
                    display:
                      this.state.input.provider === "aws" ? " block" : "none",
                  }}>
                    <Form.Label>Access Key</Form.Label>
                    <Form.Control
                      type="text"
                      onChange={this.handleChange}
                      placeholder="Access key"
                      value={this.state.input.access_key_aws_storage}
                      name="access_key"
                    />
                  </Form.Group>
                  <Form.Group className="register bg-blue" style={{
                    display:
                      this.state.input.provider === "aws" ? " block" : "none",
                  }}>
                    <Form.Label>Secret Key</Form.Label>
                    <Form.Control
                      type="text"
                      onChange={this.handleChange}
                      placeholder="Secret key"
                      value={this.state.input.secret_key_aws_storage}
                      name="secret_key"
                    />
                  </Form.Group>

                  <Button
                    type="submit"
                    className="btn btn-primary
                       col-lg-12"
                  >
                    Update
                      <FaAngleRight size={20} />
                  </Button>
                </Form>
              </div>
            </Col>
          </Row>
        </Container>
      </div>
    );
  }
}
