import React, { Component } from "react";
import {
  form,
  Navbar,
  Container,
  Col,
  Row,
  Image,
  Card,
  Button
} from "react-bootstrap";
import { FaGithub,FaYoutube,FaSpotify,FaSlackHash } from "react-icons/fa";
import { Link } from "react-router-dom";
import "./Landpage.scss";
//   import screen from './images/screen.png'

export default class Landpage extends Component {
  render() {
    return (
      <div className="Landpage">
        {/* Top Navigation Bar  */}
        <Navbar className="navbar navbar-expand-lg navbar-light sticky-top flex-md-nowrap pl-5 ">
          <div class="navbar-brand col-md-3 col-lg-2" href="#">
            <strong>x</strong>migrate
          </div>
          <button
            class="navbar-toggler position-absolute d-md-none collapsed"
            type="button"
            data-toggle="collapse"
            data-target="#sidebarMenu"
            aria-controls="sidebarMenu"
            aria-expanded="false"
            aria-label="Toggle navigation"
          >
            <span class="navbar-toggler-icon"></span>
          </button>
          <ul class="navbar-nav mr-auto pl-4">
            <li class="nav-item dropdown"></li>
          </ul>
          <form class="form-inline my-2 my-lg-0 pr-5 rightli">
            <ul class="navbar-nav">
              <li class="pr-5 ">Documentation</li>
              <li class="pr-5 ">Blog</li>
              <li class="pr-5 ">Get Started on Github</li>
            </ul>
          </form>
        </Navbar>
        <Container fluid>
          <Row className="justify-content-md-center">
            <Col md="auto" className="banner pt-5">
              <h1 className="banner-txt">
                Embracing The Open <br />
                Source Migrate
              </h1>
              <p className="lead">
                In efforts to expand our horizons,we welcom every investment-med{" "}
                <br />
                individual to join us in the Condotel Inverstment Opportunity
              </p>
              <Link className="btn btn-primary btn-md mr-1 " to="/home">
                Start Migrateing
              </Link>
              <Link className="btn btn-outline-primary btn-md " to="/home">
                Get Demo
              </Link>
            </Col>
          </Row>
          <Row className="justify-content-md-center">
            <Col md="8" className="banner pt-5">
              <div className="boxshad">
                <Image src="Assets/images/screen.png" fluid />
              </div>
            </Col>
          </Row>
          <Row className="justify-content-md-center">
            <Col md="auto" className="banner pt-5">
              <h1 className="banner-txt2">
                Our community supports flavours of infrastructure
              </h1>
              <p class="lead">
                The following on creating a direct mail advertising campaign
                have been
                <br />
                street-tested and will bring you huge money returns in a short
                period of time
              </p>
            </Col>
          </Row>
          <Row className="justify-content-md-center">
            <Col md="8" className="banner pt-5">
              <Row>
                <Col md="3">
                  <Image
                    src="Assets/images/Google_Cloud_Platform-Logo.wine.png"
                    fluid
                  />
                </Col>
                <Col md="3">
                  <Image
                    src="Assets/images/Amazon_Web_Services-Logo.wine.png"
                    fluid
                  />
                </Col>
                <Col md="3">
                  <Image
                    src="Assets/images/Microsoft_Azure-Logo.wine.png"
                    fluid
                  />
                </Col>
                <Col md="3">
                  <Image src="Assets/images/Red_Hat-Logo.wine.png" fluid />
                </Col>
              </Row>
            </Col>
          </Row>

          <Row className="HomeColo p-5 justify-content-md-center">
            <Col md="8">
              <Row>
                <Col md="6">
                  <Row>
                    <Col>
                      <h3 className="banner-txt2">
                        Multiformat Video Player
                        <br />
                        For Your Device Migrate
                      </h3>
                      <p class="lead">
                        The following on creating a direct mail advertising
                        campaign have been street-tested and will bring you huge
                        money returns in a short period of time
                      </p>
                    </Col>
                  </Row>
                  <Row>
                    <Col>
                      <h6 className="banner-txt3">Photograph a Protest</h6>
                      <p class="lead">
                        The following on creating a direct mail advertising
                        campaign have been
                      </p>
                    </Col>
                    <Col>
                      <h6 className="banner-txt3">Photograph a Protest</h6>
                      <p className="lead">
                        The following on creating a direct mail advertising
                        campaign have been
                      </p>
                    </Col>
                  </Row>
                  <Row>
                    <Col>
                      <h6 className="banner-txt3">Photograph a Protest</h6>
                      <p class="lead">
                        The following on creating a direct mail advertising
                        campaign have been
                      </p>
                    </Col>
                    <Col>
                      <h6 className="banner-txt3">Photograph a Protest</h6>
                      <p className="lead">
                        The following on creating a direct mail advertising
                        campaign have been
                      </p>
                    </Col>
                  </Row>
                </Col>
                <Col md="6">
                  <div
                    id="carouselExampleIndicators"
                    class="carousel slide"
                    data-ride="carousel"
                  >
                    <ol class="carousel-indicators">
                      <li
                        data-target="#carouselExampleIndicators"
                        data-slide-to="0"
                        class="active"
                      ></li>
                      <li
                        data-target="#carouselExampleIndicators"
                        data-slide-to="1"
                      ></li>
                      <li
                        data-target="#carouselExampleIndicators"
                        data-slide-to="2"
                      ></li>
                    </ol>
                    <div class="carousel-inner">
                      <div class="carousel-item active">
                        <Image
                          className="d-block w-100"
                          src="Assets/images/wal.jpeg"
                        />
                      </div>
                      <div class="carousel-item">
                        <Image
                          className="d-block w-100"
                          src="Assets/images/wal.jpeg"
                        />
                      </div>
                      <div class="carousel-item">
                        <Image
                          className="d-block w-100"
                          src="Assets/images/wal.jpeg"
                        />
                      </div>
                    </div>
                  </div>
                </Col>
              </Row>
            </Col>
          </Row>

          {/* Twitter */}
          <Row>
            <Col class=" pt-5">
              <div className="card-group mainCarddiv">
                <div className="card border-light cardshadow m-3">
                  <div className="card-body">
                    <h5 className="card-title">Light card title</h5>
                    <p className="card-text lead">
                      Some quick example text to build on the card title and
                      make up the bulk of the card's content.
                    </p>
                  </div>
                </div>
                <div className="card border-light cardshadow m-3">
                  <div className="card-body">
                    <h5 className="card-title">Light card title</h5>
                    <p className="card-text lead">
                      Some quick example text to build on the card title and
                      make up the bulk of the card's content.
                    </p>
                  </div>
                </div>
                <div className="card border-light cardshadow m-3">
                  <div className="card-body">
                    <h5 className="card-title">Light card title</h5>
                    <p className="card-text lead">
                      Some quick example text to build on the card title and
                      make up the bulk of the card's content.
                    </p>
                  </div>
                </div>
                <div className="card border-light cardshadow m-3">
                  <div className="card-body">
                    <h5 className="card-title">Light card title</h5>
                    <p className="card-text lead">
                      Some quick example text to build on the card title and
                      make up the bulk of the card's content.
                    </p>
                  </div>
                </div>
              </div>
              <div className="card-group mainCarddiv">
                <div className="card border-light cardshadow m-3">
                  <div className="card-body">
                    <h5 className="card-title">Light card title</h5>
                    <p className="card-text lead">
                      Some quick example text to build on the card title and
                      make up the bulk of the card's content.
                    </p>
                  </div>
                </div>
                <div className="card border-light cardshadow m-3">
                  <div className="card-body">
                    <h5 className="card-title">Light card title</h5>
                    <p className="card-text lead">
                      Some quick example text to build on the card title and
                      make up the bulk of the card's content.
                    </p>
                  </div>
                </div>
                <div className="card border-light cardshadow m-3">
                  <div className="card-body">
                    <h5 className="card-title">Light card title</h5>
                    <p className="card-text lead">
                      Some quick example text to build on the card title and
                      make up the bulk of the card's content.
                    </p>
                  </div>
                </div>
                <div className="card border-light cardshadow m-3">
                  <div className="card-body">
                    <h5 className="card-title">Light card title</h5>
                    <p className="card-text lead">
                      Some quick example text to build on the card title and
                      make up the bulk of the card's content.
                    </p>
                  </div>
                </div>
              </div>
            </Col>
          </Row>

          {/* Community */}
          <div className="HomeColo justify-content-md-center p-5">
            <Row>
              <Col md="12" className="banner pt-5">
                <h1 className="banner-txt2">
                  Learn more and get involved with community
                </h1>
                <p className="lead">
                  Join the conversation and help shape the evolution of
                  <br />
                  Crossplane.Here are fews ways to get started
                </p>
              </Col>
            </Row>
            <Row className="justify-content-md-center">
              <Col md="auto" >
                <Card style={{ width: "10rem" }} className="shadow border-light px-3">
                  <Card.Body className="iconcard"><FaSlackHash size={50}/>Slack</Card.Body>
                </Card>
                <Button className="mt-3 txtbtn"variant="outline-primary" size="md" block>JOIN SLACK</Button>
              </Col>
              <Col md="auto" >
             
                <Card style={{ width: "10rem" }} className="shadow border-light px-3">
                  <Card.Body className="iconcard"><FaYoutube size={50}/>Youtube</Card.Body>
                 
                </Card>
                <Button className="mt-3 txtbtn"variant="outline-primary" size="md" block>VISIT YOUTUBE</Button>
              </Col>
        
              <Col md="auto" >
             
             <Card style={{ width: "10rem" }} className="shadow border-light px-3">
               <Card.Body className="iconcard"><FaGithub size={50}/>Github</Card.Body>
              
             </Card>
             <Button className="mt-3 txtbtn"variant="outline-primary" size="md" block>VISIT GITHUB</Button>
           </Col>
           <Col md="auto" >
             
             <Card style={{ width: "10rem" }} className="shadow border-light px-3">
               <Card.Body className="iconcard"><FaSpotify size={50}/>Spotify</Card.Body>
              
             </Card>
             <Button className="mt-3 txtbtn"variant="outline-primary" size="md" block>VISIT SPOTIFY</Button>
           </Col>
          
            </Row>
            <Row className="justify-content-md-center">
             
              <Col md="auto" className="banner pt-5">
                <p class="lead">
                 You can also join us every other week for our community meeting call to dicuss <strong>xmigrate</strong>
                
                </p>
              </Col>
            </Row>
          </div>
          {/* Footer */}
          <Row className="justify-content-md-center">
            <Col md="8">
              <Row>
                <p className="footer-brand pt-3">
                  <strong>x</strong>migrate
                </p>
              </Row>
              <hr />
              <Row>
                <ul className="footer-list lead">
                  <li>Terms</li>
                  <li>promo</li>
                  <li>Download</li>
                  <li>News</li>
                </ul>
              </Row>
            </Col>
          </Row>
        </Container>
      </div>
    );
  }
}
