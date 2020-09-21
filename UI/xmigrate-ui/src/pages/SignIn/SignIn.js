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
    this.state = {}
  }



  Changemail(e){
    this.setState({email:e.target.value});
    console.log(e.target.value);
  }

  ChangePass(e){
    this.setState({pass:e.target.value});
  }
  ClikedLogin(e){
    e.preventDefault();
    // var data={
    //   "username":this.state.email,
    //   "password":this.state.password
    // }
    // PostService(LOGIN, data).then((data) => {
    //   console.log(data)
    // })
    Auth.login(() => {
      this.props.history.push("/home");

    })
    
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
                 
                   <Form className="FormStyle">
                    <Form.Group className="register bg-blue">
                      <Form.Label >Email Id</Form.Label>
                      <Form.Control
                        type="text"
                        onChange = {this.Changemail.bind(this)}
                        id="exampleInputEmail1"
                        aria-describedby="emailHelp"
                        placeholder="Enter email"
                        name="email"
                      />
                    </Form.Group>
                    <Form.Group>
                      <Form.Label >
                        Password
                      </Form.Label>
                      <Form.Control
                        type="password"
                        onChange = {this.ChangePass.bind(this)}
                        id="exampleInputPassword1"
                        placeholder="Password"
                        name="password"
                      />
                    </Form.Group>
                    <Button
                      type="submit"
                      className="btn btn-secondary col-lg-12"
                      onClick={this.ClikedLogin.bind(this)}
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
