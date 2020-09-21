import React, { Component } from 'react'
import { Link } from 'react-router-dom'
import * as icon from 'react-icons/all'
import "./HeaderComponent.scss"
import Auth from '../../services/Auth'
export default class HeaderComponent extends Component {
    logout(e){
        Auth.logout(()=>{
        })   
    }
    
    render() {
        return (
            <div className="HeaderComponent">
                <nav className="navbar navbar-expand-lg navbar-light sticky-top bg-light flex-md-nowrap p-0 ">
                    <Link className="navbar-brand col-md-3 col-lg-2" to="">
                        <img className="w-60" src="/Assets/images/logo/logo.png" alt="xmigrate"/>
                    </Link>
                    <button className="navbar-toggler position-absolute d-md-none collapsed" type="button" data-toggle="collapse"
                        data-target="#sidebarMenu" aria-controls="sidebarMenu" aria-expanded="false" aria-label="Toggle navigation">
                        <span className="navbar-toggler-icon"></span>
                    </button>
                    <ul className="navbar-nav mr-auto pl-4">
                        <li className="nav-item dropdown">
                            <Link className="nav-link dropdown-toggle btnnavlink px-3 py-1" to="" id="navbarDropdown" role="button"
                                data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                                ProjectSeOps   </Link>

                            <div className="dropdown-menu" aria-labelledby="navbarDropdown">
                                <Link className="dropdown-item" to="">Action</Link>
                                <Link className="dropdown-item" to="">Another action</Link>
                                <div className="dropdown-divider"></div>
                                <Link className="dropdown-item" to="">Something else here</Link>
                            </div>
                        </li>
                        <li className="nav-item pl-2">
                            <Link className="nav-link btngrid px-2 py-1 text-white " to="">
                                <icon.FiMenu />
                            </Link>
                        </li>
                    </ul>
                    <form className="form-inline my-2 my-lg-0">
                        <ul className="navbar-nav">
                            <li className="pr-4">
                                <Link to="">
                                    <icon.FiMessageSquare />
                                </Link>
                            </li>
                            <li className="pr-4">
                                <Link to="">
                                    <icon.FiBell />
                                </Link>
                            </li>
                        </ul>
                        {/* <!-- Right side buttons Navigation bar --> */}
                        <div className="right-style">
                            <ul className="navbar-nav">
                                <li className="nav-item dropdown">
                                    <Link className="nav-link dropdown-toggle" to="" id="navbarDropdownMenuLink" role="button"
                                        data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">

                                        <icon.FaUserAstronaut />
                                        {/* <img src="photo-1556470234-36a5389f905a.jpg" width="40" height="40" className="rounded-circle" /> */}
                                                Reon Saji
                                        </Link>


                                    <div className="dropdown-menu" aria-labelledby="navbarDropdownMenuLink">
                                        <Link className="dropdown-item listitemscol" to="">Dashboard</Link>
                                        <Link className="dropdown-item listitemscol" to="">Edit Profile</Link>
                                        <Link className="dropdown-item listitemscol" to="/" onClick={this.logout.bind(this)}>Log Out</Link>
                                    </div>
                                </li>
                            </ul>
                        </div>
                    </form>
                </nav>
            </div>
        )
    }
}
