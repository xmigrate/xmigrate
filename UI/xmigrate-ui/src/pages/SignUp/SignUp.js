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
import { FaAngleRight } from "react-icons/fa";
import "./SignUp.scss";
import PostService from '../../services/PostService';
import { SIGNUP } from '../../services/Services';

export default class SignUp extends Component {
  constructor(props) {
    super();
    let input = {};
    input["name"] = "";
    input["password"] = "";                                                                                                                           
    input["confirm_password"] = "";
    this.state = {
      input:input,
      errors:{}
    };
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

  async handleSubmit(event) {
    event.preventDefault();
    if(this.validate()){
        console.log(this.state);
           var data={
      "username":this.state.input["name"],
      "password":this.state.input["password"]
    }
    console.log(data);
    //Posting to server
    await PostService(SIGNUP, data).then((data) => {
      let input = {};
      input["name"] = "";
      input["email"] = "";
      input["password"] = "";
      input["confirm_password"] = "";
      this.setState({input:input});
      alert('Form is submited');
      console.log(data)
      this.props.history.push("/");
    })
    
    }
  }

  validate(){
    let input = this.state.input;
    let errors = {};
    let isValid = true;

    if (!input["name"]) {
      isValid = false;
      errors["name"] = "Please enter your UserId.";
    }


    if (!input["password"]) {
      isValid = false;
      errors["password"] = "Please enter your password.";
    }

    if (!input["confirm_password"]) {
      isValid = false;
      errors["confirm_password"] = "Please enter your confirm password.";
    }
    if (typeof input["password"] !== "undefined" && typeof input["confirm_password"] !== "undefined") {     
      if (input["password"] !== input["confirm_password"]) {
        isValid = false;
        errors["password"] = "Passwords don't match.";
      }
    } 

    this.setState({
      errors: errors
    });
    return isValid;
}

  render() {
    return (
      <div className="SignUp h-100">
        <MainHeaderComponent />
        {/* Top Navigation Bar  */}
        <Container className="h-100">
          <Row className=" h-100 justify-content-center align-items-center">
            <Col md="5">
              <Card className="CardSingin">
                 <Card.Header className="card-head">
                  <h3>Sign Up</h3>
                  <p className="sub">Cloud migration made easy</p>
                </Card.Header>
               <Card.Body>
                 
                   <Form className="FormStyle" onSubmit={this.handleSubmit}>
                    <Form.Group className="register bg-blue">
                      <Form.Label >User Id</Form.Label>
                      <Form.Control
                        type="text"
                        name="name"
                        value={this.state.input.name}
                        onChange={this.handleChange}
                        id="name"
                        aria-describedby="nameHelp"
                        placeholder="Enter Userid"
                      />
                    </Form.Group>
                    <div className="text-danger">{this.state.errors.name}</div>
                    <Form.Group>
                      <Form.Label >
                        Password
                      </Form.Label>
                      <Form.Control
                        type="password"
                        value={this.state.input.password}
                        onChange={this.handleChange}
                        id="exampleInputPassword1"
                        placeholder="Password"
                        name="password"
                      />
                    </Form.Group>
                    <div className="text-danger">{this.state.errors.password}</div>
                    <Form.Group>
                      <Form.Label >
                        Re-enter Password
                      </Form.Label>
                      <Form.Control
                        type="password"
                        name="confirm_password" 
                        value={this.state.input.confirm_password}
                        onChange={this.handleChange}
                        id="exampleInputPassword1"
                        placeholder="Re Enter Password"
                      />
                    </Form.Group>
                    <div className="text-danger">{this.state.errors.confirm_password}</div>
                    <Button
                      type="submit"
                      className="btn btn-secondary col-lg-12"
                    >
                      Sign Up<FaAngleRight size={20}/>
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
