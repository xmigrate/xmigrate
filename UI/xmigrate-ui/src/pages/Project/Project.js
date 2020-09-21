import React, { Component } from "react";
import {
  Form,
  Container,
  Col,
  Row,
  Card,
  Button
} from "react-bootstrap";
import MainHeaderComponent from "../../components/MainHeaderComponent/MainHeaderComponent";
import { FaAngleRight,FaAws,FaCloud } from "react-icons/fa";
import { SiMicrosoftazure,SiGooglecloud } from "react-icons/si";
import "./Project.scss";
//   import screen from './images/screen.png'

export default class Project extends Component {
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
                 
                   <Form className="FormStyle">
                    <Form.Group className="register bg-blue">
                      <Form.Label >Project Name</Form.Label>
                      <Form.Control
                        type="text"
                       
                        id="exampleInputEmail1"
                        aria-describedby="emailHelp"
                        placeholder="Add Name"
                        name="email"
                      />
                    </Form.Group>
                    <Form.Group className="register bg-blue">
                      <Form.Label >Select Location</Form.Label>
                      <Form.Control
                        type="text"
                       
                        id="exampleInputEmail1"
                        aria-describedby="emailHelp"
                        placeholder="Select Location"
                        name="Locaiton"
                      />
                    </Form.Group>
                    <Form.Group className="register bg-blue">
                      <Form.Label >Subscription</Form.Label>
                      <Form.Control
                        type="text"
                       
                        id="exampleInputEmail1"
                        aria-describedby="emailHelp"
                        placeholder="Subscription id"
                        name="Subscription"
                      />
                    </Form.Group>
                    <Form.Group>
                      <Form.Label >
                        Select Provider
                      </Form.Label>
                    </Form.Group>
      <Row className="Providerrow">
        <Col className="ProviderCol">
        <Card>
          <Card.Body className="Provider">
          <FaAws size={50} />
          </Card.Body>
        </Card>
        </Col>
        <Col className="ProviderCol">
        <Card >
          <Card.Body className="Provider">
          <SiMicrosoftazure size={50} />
             
          </Card.Body>
        </Card>
        </Col>
        <Col className="ProviderCol">
        <Card>
          <Card.Body className="Provider">
          <SiGooglecloud size={50} />
          </Card.Body>
        </Card>
        </Col>
        </Row>

                    <Button
                      type="submit"
                      className="btn btn-primary
                       col-lg-12"
                    >
                      Create Project<FaAngleRight size={20}/>
              
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
