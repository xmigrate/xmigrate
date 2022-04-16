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
      console.log(res);
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
               <Card.Body className="p-0 pb-4">
                 <div className="spaceCard">
                   <Form className="FormStyle" onSubmit={this.handleSubmit}>
                    <Form.Group className="register bg-blue">
                      <Form.Label >User Name</Form.Label>
                      <Form.Control
                        type="text"
                        value={this.state.input.UserId}
                        onChange={this.handleChange}
                        id="exampleInputEmail1"
                        aria-describedby="emailHelp"
                        placeholder="User Name"
                        name="UserId"
                      />
                    </Form.Group>
                    <Form.Group className="passSpa">
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
                      className="btn btn-secondary col-lg-12 login"
                    >
                      Login   <span className="iconLogin"><FaAngleRight size={20}/></span>
                    </Button>
                    <div className="text-danger">{this.state.errors.Authentication}{}</div>
                    <div>
                    <div className="forgotPassword float-left">
                      <span className=" btn text-muted pl-0">Forgot Password?</span>
                    </div>
                    <div className="forgotPassword float-right">
                    <Link  to="/SignUp" >
                      <span className="btn text-muted pr-0">SignUp</span>
                      </Link>
                    </div>
                    </div>
                  </Form>  
                  </div>
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
