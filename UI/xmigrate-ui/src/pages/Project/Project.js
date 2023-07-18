import React, { Component } from "react";
import { Form, Container, Col, Row, Card, Button } from "react-bootstrap";
import MainHeaderComponent from "../../components/MainHeaderComponent/MainHeaderComponent";
import { FaAngleRight, FaAws, 
  FaCloud
 } from "react-icons/fa";
import { SiMicrosoftazure, 
   SiGooglecloud 
} from "react-icons/si";
import PostService from "../../services/PostService";
import "./Project.scss";
import {
  LOCATIONPOST,
  CREATEPROJECT,
  CREATESTORAGE,
} from "../../services/Services";
import Loader from "../../components/Loader/Loader";

export default class Project extends Component {
  constructor(props) {
    super();
    let input = {};
    input["provider"] = "";
    this.state = {
      input: input,
      status: "Verify",
      errors: {},
      locations: [],
      loader: false,
      service_account:{}
    };
    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
    this.handleFileChange = this.handleFileChange.bind(this);
  }
  handleChange(event) {
    let input = this.state.input;
    input[event.target.name] = event.target.value;
    this.setState({
      input,
    });
  }

  handleFileChange(e) {
    const cancel = !e.target.files.length;
    if (cancel) return;
    console.log(e.target.files[0]);
    const fileReader = new FileReader();
    fileReader.readAsText(e.target.files[0], "UTF-8");
    fileReader.onload = e =>{ 
      
    var GCP_Json = JSON.parse(e.target.result);
    console.log(GCP_Json);
    this.setState({service_account : GCP_Json})
  };
   console.log(this.state);
  }

  handleProvider(text) {
    let input = this.state.input;
    input["provider"] = text;
    console.log(this.state);
    this.setState({
      input,
    });
  }

  async handleSubmit(event) {
    event.preventDefault();
    console.log(this.state);
    if (this.validate()) {
      var data = {};
      if (this.state.input["provider"] === "aws") {
        data = {
          name: this.state.input["name"],
          provider: this.state.input["provider"],
          aws_secret_key: this.state.input["secret_key"],
          aws_access_key: this.state.input["access_key"],
          location: this.state.input["location"]
        };
      } else if (this.state.input["provider"] === "azure") {
        data = {
          name: this.state.input["name"],
          provider: this.state.input["provider"],
          azure_subscription_id: this.state.input["subscription_id"],
          azure_client_secret: this.state.input["secret"],
          azure_tenant_id: this.state.input["tenant_id"],
          azure_client_id: this.state.input["client_id"],
          location: this.state.input["location"],
          azure_resource_group: this.state.input["resource_group"],
        };
      } else if (this.state.input["provider"] === "gcp"){
        data = {
          name: this.state.input["name"],
          provider: this.state.input["provider"],
          gcp_service_token: this.state.service_account,
          location: this.state.input["location"]
        };
      }

      console.log(data);

      this.setState({
        loader: true,
      });
      if (this.state.status === "Verify") {
        await PostService(LOCATIONPOST, data).then((res) => {
          console.log(res.data);
            //Setting the default location as value
            let input = this.state.input;
            if(data.location === undefined){
              input["location"] = res.data.locations[0];
            }
          this.setState({
            locations: res.data.locations,
            status: "Create Project",
            loader: false,
          });
        });
      } else if (this.state.status === "Create Project") {
        console.log("Create project", data);
        await PostService(CREATEPROJECT, data).then((res) => {
          console.log(res);
          this.setState({
            status: "Storage",
            loader: false,
          });
        });
      } else if (this.state.status === "Storage") {
        var dataProvider = {};
        if (this.state.input["provider"] === "aws") {
          dataProvider = {
            //Here Make Changes
            project: this.state.input["name"],
            provider: this.state.input["provider"],
            bucket_name: this.state.input["bucket"],
            secret_key: this.state.input["secret_key"],
            access_key: this.state.input["access_key"],
          };
        } else if (this.state.input["provider"] === "azure") {
          dataProvider = {
            provider: this.state.input["provider"],
            project: this.state.input["name"],
            bucket_name: this.state.input["storage"],
            container: this.state.input["container"],
            access_key: this.state.input["access_key"],
          };
        }else if (this.state.input["provider"] === "gcp") {
          dataProvider = {
            provider: this.state.input["provider"],
            project: this.state.input["name"],
            bucket_name: this.state.input["bucket"],
            secret_key: this.state.input["secret_key"],
            access_key: this.state.input["access_key"],
          };
        }
   
        console.log("data posted", dataProvider);
        this.setState({
          loader: true,
        });
        await PostService(CREATESTORAGE, dataProvider).then((res) => {
          this.setState({
            loader: false,
          });
          console.log(res);
          if(res.status === 200){
            this.props.history.push({pathname:"/home",state:{ detail: this.state.input["name"] }});
          }
          else{
            
          }
         
        });
      }
    }
  }


  //To validate the project submit
  validate() {
    // let input = this.state.input;
    // let errors = {};
    let isValid = true;
    return isValid;
  }

  render() {
    return (
      <div className="Project h-100">
        <MainHeaderComponent />
        {/* Top Navigation Bar  */}
        <Container className="h-100">
          <Row className=" h-100 justify-content-center align-items-center">
            <Col md="6">
              <Card className="CardSingin">
                <Card.Header className="card-head">
                  <h3>Create Project</h3>
                  <p className="sub">Cloud migration made easy</p>
                </Card.Header>
                <Card.Body>
                  {this.state.loader ? <Loader /> : <span></span>}

                  <Form
                    className="FormStyle"
                    onSubmit={this.handleSubmit}
                    style={{
                      display: this.state.loader === true || this.state.status === "Storage"  ? " none" : "block",
                    }}
                  >
              
                    <Form.Group className="register bg-blue mb-3">
                      <Form.Label>Project Name</Form.Label>
                      <Form.Control
                        type="text"
                        id="exampleInputEmail1"
                        onChange={this.handleChange}
                        aria-describedby="emailHelp"
                        placeholder="Project Name"
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
                            onClick={() => this.handleProvider("aws")}
                          >
                            <FaAws size={50} />
                          </Card.Body>
                        </Card>
                      </Col>
                      <Col
                        className={
                          "ProviderCol" +
                          (this.state.input.provider === "azure"
                            ? " active"
                            : "")
                        }
                      >
                        <Card>
                          <Card.Body
                            className="Provider"
                            onClick={() => this.handleProvider("azure")}
                          >
                            <SiMicrosoftazure size={50} />
                          </Card.Body>
                        </Card>
                      </Col>
                       <Col className={"ProviderCol"+ (this.state.input.provider === "gcp" ? ' active' : '')}>
                        <Card>
                          <Card.Body className="Provider" onClick={()=>this.handleProvider("gcp")}>
                            <SiGooglecloud size={50} />
                          </Card.Body>
                        </Card>
                      </Col> 
                    </Row>

                    <Form.Group
                      className="register bg-blue mb-3"
                      style={{
                        display:
                          this.state.input.provider === "gcp"
                            ? " block"
                            : "none",
                      }}
                    >
                      <Form.Label>Upload Service Account Json File</Form.Label>
                      <Form.Control
                        type="file"
                        placeholder="Upload Json Document"
                        onChange={(e)=>this.handleFileChange(e)}
                        name="ServiceAccountJson"
                        accept=".json"
                      />
                    </Form.Group>

                    <Form.Group
                      className="register bg-blue mb-3"
                      style={{
                        display:
                          this.state.input.provider === "azure"
                            ? " block"
                            : "none",
                      }}
                    >
                      <Form.Label>Subscription Id</Form.Label>
                      <Form.Control
                        type="text"
                        onChange={this.handleChange}
                        placeholder="Subscription Id"
                        name="subscription_id"
                      />
                    </Form.Group>
                    <Form.Group
                      className="register bg-blue mb-3"
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
                        placeholder="Client Id"
                        name="client_id"
                      />
                    </Form.Group>
                    <Form.Group
                      className="register bg-blue mb-3"
                      style={{
                        display:
                          this.state.input.provider === "aws"
                            ? " block"
                            : "none",
                      }}
                    >
                      <Form.Label>Access Key</Form.Label>
                      <Form.Control
                        type="text"
                        onChange={this.handleChange}
                        placeholder="Access key"
                        name="access_key"
                      />
                    </Form.Group>
                    <Form.Group
                      className="register bg-blue mb-3"
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
                        placeholder="Secret Key"
                        name="secret"
                      />
                    </Form.Group>
                    <Form.Group
                      className="register bg-blue mb-3"
                      style={{
                        display:
                          this.state.input.provider === "aws" 
                            ? " block"
                            : "none",
                      }}
                    >
                      <Form.Label>Secret Key</Form.Label>
                      <Form.Control
                        type="text"
                        onChange={this.handleChange}
                        placeholder="Secret key"
                        name="secret_key"
                      />
                    </Form.Group>
            
                    <Form.Group
                      className="register bg-blue mb-3"
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
                        name="tenant_id"
                      />
                    </Form.Group>
                    <Form.Group
                      className="register bg-blue mb-3"
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
                        name="resource_group"
                      />
                    </Form.Group>
                    <Form.Group
                      className="register bg-blue mb-3"
                      style={{
                        display:
                          this.state.status === "Create Project"
                            ? " block"
                            : "none",
                      }}
                    >
                      <Form.Label>Select Location</Form.Label>
                      <Form.Control
                        as="select"
                        name="location"
                        onChange={this.handleChange}
                      >
                        {this.state.locations.map((location) => (
                          <option key={location} value={location}>
                            {location}
                          </option>
                        ))}
                      </Form.Control>
                    </Form.Group>

                    <Button
                      type="submit"
                      className="btn btn-primary
                       col-lg-12 mb-3"
                    >
                      {this.state.status}
                      <FaAngleRight size={20} />
                    </Button>
                  </Form>



                  {/* Form For Storage */}
                  <Form className="FormStyle"
                    onSubmit={this.handleSubmit}
                    style={{
                      display:
                        this.state.status === "Storage" && this.state.loader !== true ? " block" : "none",
                    }}
                  >
                        <Form.Group
                      className="register bg-blue mb-3"
                      style={{
                        display:
                          this.state.input.provider === "aws"  || this.state.input.provider ==="gcp"
                            ? "block"
                            : "none",
                      }}
                    >
                      <Form.Label  style={{
                        display:
                          this.state.input.provider === "aws" 
                            ? "block"
                            : "none",
                      }}>S3 Bucket</Form.Label>
                       <Form.Label  style={{
                        display:
                          this.state.input.provider === "gcp" 
                            ? "block"
                            : "none",
                      }}>GCS Bucket</Form.Label>
                      <Form.Control
                        type="text"
                        onChange={this.handleChange}
                        placeholder="S3 Bucket Name"
                        name="bucket"
                      />
                    </Form.Group>
                    <Form.Group className="register bg-blue mb-3"
                     style={{
                      display:
                        this.state.input.provider === "azure"
                          ? "block"
                          : "none",
                    }}>
                      <Form.Label>Storage</Form.Label>
                      <Form.Control
                        type="text"
                        onChange={this.handleChange}
                        placeholder="Storage"
                        name="storage"
                      />
                    </Form.Group>
                    <Form.Group className="register bg-blue mb-3"  style={{
                      display:
                        this.state.input.provider === "azure"
                          ? " block"
                          : "none",
                    }}>
                      <Form.Label>Container</Form.Label>
                      <Form.Control
                        type="text"
                        onChange={this.handleChange}
                        placeholder="Container"
                        name="container"
                      />
                    </Form.Group>
                    <Form.Group className="register bg-blue mb-3"  style={{
                      display:
                        this.state.input.provider === "azure"  || this.state.input.provider ==="gcp"
                          ? " block"
                          : "none",
                    }}>
                      <Form.Label>Access Key</Form.Label>
                      <Form.Control
                        type="text"
                        onChange={this.handleChange}
                        placeholder="Access key"
                        name="access_key"
                      />
                    </Form.Group>
                    <Form.Group
                      className="register bg-blue mb-3"
                      style={{
                        display:
                          this.state.input.provider === "gcp" 
                            ? " block"
                            : "none",
                      }}
                    >
                      <Form.Label>Secret Key</Form.Label>
                      <Form.Control
                        type="text"
                        onChange={this.handleChange}
                        placeholder="Secret key"
                        name="secret_key"
                      />
                    </Form.Group>
                   
                    <Button
                      type="submit"
                      className="btn btn-primary
                       col-lg-12"
                    >
                      Save
                      <FaAngleRight size={20} />
                    </Button>
                  </Form>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Container>
      </div>
    );
  }
}
