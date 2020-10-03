import React, { Component } from "react";
import { Form, Container, Col, Row, Card, Button } from "react-bootstrap";
import MainHeaderComponent from "../../components/MainHeaderComponent/MainHeaderComponent";
import { FaAngleRight, FaAws, FaCloud } from "react-icons/fa";
import { SiMicrosoftazure, SiGooglecloud } from "react-icons/si";
import PostService from '../../services/PostService'
import "./Project.scss";
import { LOCATIONPOST } from '../../services/Services';

export default class Project extends Component {

  constructor(props){
    super()
    let input = {};
    input["provider"] = "";                                                                                                                    
    this.state = {
      input:input,
      errors:{}
    }
    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }
  handleChange(event) {
    let input = this.state.input;
    input[event.target.name] = event.target.value;
    this.setState({
      input
    });
  }
  handleProvider(text) {
    let input = this.state.input;
    input["provider"] = text;
    console.log(this.state);
    this.setState({
      input
    });
  }

  handleSubmit(event) {
    event.preventDefault();
    console.log(this.state);
    if(this.validate()){

    if(this.state.input["provider"] ==="aws"){

      var data={
        "name":this.state.input["name"],
        "provider":this.state.input["provider"],
        "secret_key":this.state.input["secret_key"],
        "access_key":  this.state.input["access_key"],
      }

    }else if(this.state.input["provider"]==="azure"){
      var data={
        "name":this.state.input["name"],
        "provider":this.state.input["provider"],
        "subscription_id":this.state.input["subscription_id"],   
        "secret":this.state.input["secret"],
        "tenant_id":this.state.input["tenant_id"], 
        "client_id":this.state.input["client_id"]  
      }
    }

  console.log(data);
  // data = JSON.stringify(data);
     PostService(LOCATIONPOST, data).then((res) => {
      console.log(res);
    });
  
}
  }

  validate(){
    let input = this.state.input;
    let errors = {};
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
                  <Form className="FormStyle" onSubmit={this.handleSubmit}>
                    <Form.Group className="register bg-blue">
                      <Form.Label>Project Name</Form.Label>
                      <Form.Control
                        type="text"
                        id="exampleInputEmail1"
                        onChange={this.handleChange}
                        aria-describedby="emailHelp"
                        placeholder="Add Name"
                        name="name"
                      />
                    </Form.Group>
                    <Form.Group>
                      <Form.Label>Select Provider</Form.Label>
                    </Form.Group>
                    <Row className="Providerrow">
                      <Col className={"ProviderCol"+ (this.state.input.provider === "aws" ? ' active' : '')}>
                        <Card >
                          <Card.Body className="Provider" onClick={()=>this.handleProvider("aws")}>
                            <FaAws size={50} />
                          </Card.Body>
                        </Card>
                      </Col>
                      <Col className={"ProviderCol"+ (this.state.input.provider === "azure" ? ' active' : '')}>
                        <Card>
                          <Card.Body className="Provider"  onClick={()=>this.handleProvider("azure")}>
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
            
                    <Form.Group className="register bg-blue" style={{display: this.state.input.provider === "azure" ? ' block' : 'none'}}>
                      <Form.Label>Subscription</Form.Label>
                      <Form.Control
                        type="text"
                        onChange={this.handleChange}
                        placeholder="Subscription id"
                        name="subscription_id"
                      />
                    </Form.Group>
                    <Form.Group className="register bg-blue" style={{display: this.state.input.provider === "azure" ? ' block' : 'none'}}>
                      <Form.Label>Client Id</Form.Label>
                      <Form.Control
                        type="text"
                        onChange={this.handleChange}
                        placeholder="Client id"
                        name="client_id"
                      />
                    </Form.Group>
             
                 
                    <Form.Group className="register bg-blue"style={{display: this.state.input.provider === "azure" ? ' block' : 'none'}}>
                      <Form.Label>Secret Key</Form.Label>
                      <Form.Control
                        type="text"
                        onChange={this.handleChange}
                        placeholder="secret_key"
                        name="secret"
                      />
                    </Form.Group>
                    <Form.Group className="register bg-blue" style={{display: this.state.input.provider === "aws" ? ' block' : 'none'}}>
                      <Form.Label>Secret Key</Form.Label>
                      <Form.Control
                        type="text"
                        onChange={this.handleChange}
                        placeholder="Secret key"
                        name="secret_key"
                      />
                    </Form.Group>
                    <Form.Group className="register bg-blue" style={{display: this.state.input.provider === "aws" ? ' block' : 'none'}}>
                      <Form.Label>Access Key</Form.Label>
                      <Form.Control
                        type="text"
                        onChange={this.handleChange}
                        placeholder="Access key"
                        name="access_key"
                      />
                    </Form.Group>
                    <Form.Group className="register bg-blue"style={{display: this.state.input.provider === "azure" ? ' block' : 'none'}}>
                      <Form.Label>Tenat Id</Form.Label>
                      <Form.Control
                        type="text"
                        onChange={this.handleChange}
                        placeholder="Tenant Id"
                        name="tenant_id"
                      />
                    </Form.Group>
                                      {/* <Form.Group className="register bg-blue" style={{display: this.state.input.provider === "Azure" ? ' block' : 'none'}}>
                      <Form.Label>Resource Group</Form.Label>
                      <Form.Control
                        type="text"

                        onChange={this.handleChange}
                        placeholder="Resource Group"
                        name="resource_group"
                      />
                    </Form.Group> */}
                    {/* <Form.Group className="register bg-blue" >
                      <Form.Label>Select Location</Form.Label>
                      <Form.Control
                        type="text"
                        onChange={this.handleChange}
                        placeholder="Select Location"
                        name="location"
                      />
                    </Form.Group> */}

                    <Button
                      type="submit"
                      className="btn btn-primary
                       col-lg-12"
                    >
                      Create Project
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
