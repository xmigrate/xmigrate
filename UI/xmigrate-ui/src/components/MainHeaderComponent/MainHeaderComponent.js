import React, { Component } from 'react'
import {
    Navbar,
  } from "react-bootstrap";
import { Link } from 'react-router-dom'
import "./MainHeaderComponent.scss"
export default class MainHeaderComponent extends Component {
    render() {
        return (
            <div className="MainHeaderComponent">
        <Navbar className="navbar  navbar-default navbar-expand-lg navbar-light fixed-top">
          <div className="navbar-brand col-md-3 col-lg-2" href="#">
            <strong>x</strong>migrate
          </div>
          <button
            className="navbar-toggler position-absolute d-md-none collapsed"
            type="button"
            data-toggle="collapse"
            data-target="#sidebarMenu"
            aria-controls="sidebarMenu"
            aria-expanded="false"
            aria-label="Toggle navigation"
          >
            <span className="navbar-toggler-icon"></span>
          </button>
          <ul className="navbar-nav mr-auto pl-4">
            <li className="nav-item dropdown"></li>
          </ul>
        </Navbar>
            </div>
        )
    }
}
