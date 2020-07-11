import React, { Component } from 'react'
import { Container, Row, Col, Form, Button } from 'react-bootstrap'

export default class Discover extends Component {
    render() {
        return (
            <div className="Discover media-body background-primary ">
                <Container className="py-5 ">
                    <h4 className="p-0 m-0">
                        Add IP’s of your servers to be migrated
                    </h4>

                    <Row className="py-5 ">
                        <Col md={{ span: 5 }} className="bg-white shadow-sm rounded">
                            <div className="p-3 d-flex flex-column justify-content-between h-100">

                                <h5>
                                    Server IP's
                                </h5>
                                <input type="textarea" name="" id="" />

                                <Form className="py-4">
                                    <Form.Group controlId="formBasicEmail">
                                        <Form.Label>Username</Form.Label>
                                        <Form.Control type="text" placeholder="User shouls have sudo access" />
                                        {/* <Form.Text className="text-muted">
                                        We'll never share your email with anyone else.
                                    </Form.Text> */}
                                    </Form.Group>

                                    <Form.Group controlId="formBasicPassword">
                                        <Form.Label>Password</Form.Label>
                                        <Form.Control type="password" placeholder="Enter the password to be used" />
                                    </Form.Group>
                                    {/* <Form.Group controlId="formBasicCheckbox">
                                    <Form.Check type="checkbox" label="Check me out" />
                                </Form.Group> */}
                                    <Button variant="primary" type="submit" className="w-100">
                                        Submit
                                    </Button>
                                </Form>

                            </div>
                        </Col>
                        <Col md={{ span: 6, offset: 1 }} className="shadow-sm rounded bg-white d-flex flex-column p-0">
                            <div className="p-3 d-flex justify-content-between">
                                <span>
                                    Lorem Ipsum Dollar
                                </span>
                                <Button variant="secondary" disabled>
                                    Discover
                                </Button>
                            </div>

                            <div className="background-primary media-body p-3" style={{ overflowY: "scroll", maxHeight:"400px" }}>
                                Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque vulputate eros orci, sed varius justo eleifend ac. Sed auctor diam sit amet venenatis pulvinar. Nam nec pellentesque dolor, sit amet viverra neque. Nulla gravida enim sit amet tristique placerat. Nullam vitae massa a nisi aliquet maximus. Curabitur sit amet nisl est. Vestibulum volutpat scelerisque lectus quis fermentum. Aenean luctus vestibulum sapien, ut suscipit ligula fringilla sit amet. Proin eget sapien at turpis sodales iaculis et id nibh. Cras sodales feugiat ante ac euismod. Morbi aliquam nec dolor vitae luctus. Nam lacinia finibus tortor id facilisis. Nunc mollis, elit iaculis luctus dictum, elit mauris placerat lorem, et consectetur quam orci eu quam.

                                Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Proin varius posuere enim sed sagittis. Nunc iaculis sem sem, in sagittis nisl porta in. Ut tincidunt turpis sit amet ante euismod condimentum. Integer semper imperdiet tincidunt. Pellentesque viverra efficitur nisl, id eleifend felis maximus a. Suspendisse ultrices posuere neque, id laoreet nisl hendrerit in. Nullam vulputate condimentum erat. Phasellus porta eu metus eget auctor. Fusce dictum dui sit amet metus porta auctor. Donec sodales lorem eget lorem tincidunt dictum. Suspendisse et molestie urna, quis sodales est. Nunc vitae libero tempor, molestie risus ac, porta risus.

                                Mauris sed mi at quam pharetra maximus. Sed congue tempor purus, sit amet dignissim libero imperdiet ac. Maecenas posuere, urna vel bibendum lacinia, nisl tellus aliquet diam, eget consectetur tellus metus id velit. Aliquam tempor in risus vitae gravida. Curabitur elementum lacinia diam in tincidunt. Vestibulum iaculis fringilla felis, sit amet condimentum purus hendrerit vitae. Aenean vestibulum erat lectus, sed tempus lacus laoreet quis. Etiam fringilla ligula sapien, ut efficitur nisi pharetra sed.

                                Integer fermentum, velit sagittis facilisis aliquet, mi ante malesuada massa, ut dictum velit tellus sed sapien. Sed cursus scelerisque ligula sit amet volutpat. Ut vitae turpis ornare, cursus lectus a, elementum odio. Nam facilisis magna ac diam luctus euismod. Etiam et efficitur massa. Vestibulum posuere convallis pellentesque. Nunc non viverra lectus, sed convallis eros. Sed lobortis porttitor ultricies. Pellentesque faucibus tristique dui vitae placerat. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; Praesent ante risus, congue sed ipsum at, euismod elementum odio. Suspendisse eu magna mi. Ut sit amet dolor eget sapien venenatis viverra. Maecenas in egestas nibh, non dapibus nisi. Sed ultrices, sapien eu blandit venenatis, justo est lacinia nisi, eget scelerisque sapien diam at justo.

                                Fusce est felis, eleifend vel urna sit amet, ornare ullamcorper urna. Sed eleifend mattis mi, eget fringilla dui pulvinar iaculis. Pellentesque vehicula urna sed est fringilla, at volutpat orci molestie. Donec quam leo, consequat ut est ut, facilisis viverra mauris. Interdum et malesuada fames ac ante ipsum primis in faucibus. Curabitur vitae semper risus. Curabitur vestibulum consectetur purus id fringilla. Proin tincidunt leo ut purus blandit, vitae pharetra justo eleifend. Quisque dapibus nunc purus, egestas viverra est varius ac. Mauris fringilla venenatis euismod.
                            </div>
                        </Col>
                    </Row>

                </Container>
            </div>
        )
    }
}
