import React, { Component } from "react";
import { Form, Container, Col, Row, Card, Button } from "react-bootstrap";
import MainHeaderComponent from "../../components/MainHeaderComponent/MainHeaderComponent";
import { FaAngleRight, FaAws, FaCloud } from "react-icons/fa";
import { SiMicrosoftazure, SiGooglecloud } from "react-icons/si";
import "./Project.scss";
//   import screen from './images/screen.png'

export default class Project extends Component {

  constructor(props){
    super()
    let input = {};
    input["ProjectName"] = "";
    input["Provider"] = "";   
    input["Location"] = ""; 
    input["Subscription"] = "";   
    input["ResourceGroup"]="" ;
    input["Secret_key"]="";
    input["Access_key"]="";                                                                                                                       
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
    input["Provider"] = text;
    console.log(this.state);
    this.setState({
      input
    });
  }

  handleSubmit(event) {
    event.preventDefault();
    console.log(this.state);
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
                        name="ProjectName"
                      />
                    </Form.Group>
                    <Form.Group>
                      <Form.Label>Select Provider</Form.Label>
                    </Form.Group>
                    <Row className="Providerrow">
                      <Col className={"ProviderCol"+ (this.state.input.Provider === "AWS" ? ' active' : '')}>
                        <Card >
                          <Card.Body className="Provider" onClick={()=>this.handleProvider("AWS")}>
                            <FaAws size={50} />
                          </Card.Body>
                        </Card>
                      </Col>
                      <Col className={"ProviderCol"+ (this.state.input.Provider === "Azure" ? ' active' : '')}>
                        <Card>
                          <Card.Body className="Provider"  onClick={()=>this.handleProvider("Azure")}>
                            <SiMicrosoftazure size={50} />
                          </Card.Body>
                        </Card>
                      </Col>
                      {/* <Col className={"ProviderCol"+ (this.state.input.Provider == "GoogleCloud" ? ' active' : '')}>
                        <Card>
                          <Card.Body className="Provider" onClick={()=>this.handleProvider("GoogleCloud")}>
                            <SiGooglecloud size={50} />
                          </Card.Body>
                        </Card>
                      </Col> */}
                    </Row>
            
                    <Form.Group className="register bg-blue" style={{display: this.state.input.Provider === "Azure" ? ' block' : 'none'}}>
                      <Form.Label>Subscription</Form.Label>
                      <Form.Control
                        type="text"
                        onChange={this.handleChange}
                        placeholder="Subscription id"
                        name="Subscription"
                      />
                    </Form.Group>
                    <Form.Group className="register bg-blue" style={{display: this.state.input.Provider === "Azure" ? ' block' : 'none'}}>
                      <Form.Label>Resource Group</Form.Label>
                      <Form.Control
                        type="text"

                        onChange={this.handleChange}
                        placeholder="Resource Group"
                        name="ResourceGroup"
                      />
                    </Form.Group>
                    <Form.Group className="register bg-blue" >
                      <Form.Label>Select Location</Form.Label>
                      <Form.Control
                        type="text"
                        onChange={this.handleChange}
                        placeholder="Select Location"
                        name="Location"
                      />
                    </Form.Group>
                    <Form.Group className="register bg-blue" style={{display: this.state.input.Provider === "AWS" ? ' block' : 'none'}}>
                      <Form.Label>Access Key</Form.Label>
                      <Form.Control
                        type="text"
                        onChange={this.handleChange}
                        placeholder="access_key"
                        name="Access_key"
                      />
                    </Form.Group>
                    <Form.Group className="register bg-blue"style={{display: this.state.input.Provider === "AWS" ? ' block' : 'none'}}>
                      <Form.Label>Secret Key</Form.Label>
                      <Form.Control
                        type="text"
                        onChange={this.handleChange}
                        placeholder="secret_key"
                        name="Secret_key"
                      />
                    </Form.Group>

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
