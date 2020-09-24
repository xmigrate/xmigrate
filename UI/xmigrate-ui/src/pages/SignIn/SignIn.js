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
import "./SignIn.scss";
import PostService from '../../services/PostService';
import { LOGIN } from '../../services/Services';
import Auth from '../../services/Auth';

export default class SignIn extends Component {
  constructor(props){
    super()
    let input = {};
    input["UserId"] = "";
    input["password"] = "";                                                                                                                           
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

  async handleSubmit(event) {
    event.preventDefault();
    if(this.validate()){
        console.log(this.state);
           var data={
      "username":this.state.input["UserId"],
      "password":this.state.input["password"]
    }
    console.log(data);
    //Posting to server
    await PostService(LOGIN, data).then((res) => {
      let input = {};
      input["UserId"] = "";
      input["password"] = "";
      this.setState({input:input});
      let k = res.data;
      console.log(k.access_token);
      localStorage.setItem('auth_token', k.access_token);
      Auth.login(() => {
        this.props.history.push("/home");
      })
    })
    
    }
  }

  validate(){
    let input = this.state.input;
    let errors = {};
    let isValid = true;

    if (!input["UserId"]) {
      isValid = false;
      errors["UserId"] = "Please enter your UserId.";
    }


    if (!input["password"]) {
      isValid = false;
      errors["password"] = "Please enter your password.";
    }

 

    this.setState({
      errors: errors
    });
    return isValid;
}


  render() {
    return (
      <div className="SignIn h-100">
        <MainHeaderComponent />
        {/* Top Navigation Bar  */}
        <Container className="h-100">
          <Row className=" h-100 justify-content-center align-items-center">
            <Col md="5">
              <Card className="CardSingin">
                 <Card.Header className="card-head">
                  <h3>Sign In</h3>
                  <p className="sub">Cloud migration made easy</p>
                </Card.Header>
               <Card.Body>
                 
                   <Form className="FormStyle" onSubmit={this.handleSubmit}>
                    <Form.Group className="register bg-blue">
                      <Form.Label >User Id</Form.Label>
                      <Form.Control
                        type="text"
                        value={this.state.input.UserId}
                        onChange={this.handleChange}
                        id="exampleInputEmail1"
                        aria-describedby="emailHelp"
                        placeholder="Enter email"
                        name="UserId"
                      />
                    </Form.Group>
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
                    <Button
                      type="submit"
                      className="btn btn-secondary col-lg-12"
                    >
                      Login<FaAngleRight size={20}/>
                    </Button>
                    <div className="forgotPassword">
                      <span className="btn text-muted">Forgot Password?</span>
                    </div>
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
