import React, { Component } from "react";
import {
  Form,
  Container,
  Col,
  Row,
  Card,
  Button,
  Alert
} from "react-bootstrap";
import { Link } from 'react-router-dom'
import MainHeaderComponent from "../../components/MainHeaderComponent/MainHeaderComponent";
import Loader from '../../components/Loader/Loader'
import { FaAngleRight } from "react-icons/fa";
import "./SignIn.scss";
import PostService from '../../services/PostService';
import { LOGIN,GETPROJECTS } from '../../services/Services';
import Auth from '../../services/Auth';
import GetService from '../../services/GetService';

export default class SignIn extends Component {
  constructor(props){
    super()
    let input = {};
    input["UserId"] = "";
    input["password"] = "";
    let  sh = false;  
    if(props.location.state !== undefined){
      sh = props.location.state.show
    }                                                                                                                       
    this.state = {
      input:input,
      loader:false,
      show: sh,
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
    let errors ={};
    event.preventDefault();
    if(this.validate()){
        console.log(this.state);
           var data={
      "username":this.state.input["UserId"],
      "password":this.state.input["password"]
    }
    console.log(data);
    //Posting to server
    this.setState({
      loader:true,
    });
    await PostService(LOGIN, data).then((res) => {
      let input = {};
      if(res===401){
        errors["Authentication"] = "Invalid Authentication";
        input["UserId"] = "";
        input["password"] = "";
        this.setState({
          input:input,
          errors:errors,
          loader:false
        });
      }
      else{
      let input = {};
      input["UserId"] = "";
      input["password"] = "";
      this.setState({input:input});
      let k = res.data;
      console.log(k.access_token);
      localStorage.setItem('auth_token', k.access_token);
      
       GetService(GETPROJECTS).then((res)=>{
        this.setState({
          loader:false,
        });
        console.log("Summiting",);
        if(JSON.parse(res.data).length === 0){
          Auth.login(() => {
            this.props.history.push("/project");
          })
        }
        else{
          Auth.login(() => {
            this.props.history.push("/home");
          })
        }
      })
    }
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
    if(this.state.loader){
     return <Loader/>
    }
    else{
    return (
      <div className="SignIn h-100">
        <MainHeaderComponent />
        {/* Top Navigation Bar  */}
     

        <Container className="h-100">
          <Row className=" h-100 justify-content-center align-items-center">
            <Col md="5">
            {this.state.show?(
        <Alert  variant='success'  >
       User Created Successfully !! Please login with username and password
      </Alert>):""
        }
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
                    <div className="text-danger">{this.state.errors.Authentication}</div>
                    <div>
                    <div className="forgotPassword float-left">
                      <span className="btn text-muted">Forgot Password?</span>
                    </div>
                    <div className="forgotPassword float-right">
                    <Link  to="/SignUp" >
                      <span className="btn text-muted">SignUp</span>
                      </Link>
                    </div>
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
}
