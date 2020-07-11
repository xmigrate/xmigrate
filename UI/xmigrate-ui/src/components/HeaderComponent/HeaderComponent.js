import React, { Component } from 'react'
import { Link } from 'react-router-dom'
import * as icon from 'react-icons/all'
import "./HeaderComponent.scss"
export default class HeaderComponent extends Component {
    render() {
        return (
            <div className="HeaderComponent">
                <nav className="navbar navbar-expand-lg navbar-light sticky-top bg-light flex-md-nowrap p-0 ">
                    <Link className="navbar-brand col-md-3 col-lg-2" href="">
                        <img className="w-60" src="/Assets/images/logo/logo.png" alt="xmigrate"/>
                    </Link>
                    <button className="navbar-toggler position-absolute d-md-none collapsed" type="button" data-toggle="collapse"
                        data-target="#sidebarMenu" aria-controls="sidebarMenu" aria-expanded="false" aria-label="Toggle navigation">
                        <span className="navbar-toggler-icon"></span>
                    </button>
                    <ul className="navbar-nav mr-auto pl-4">
                        <li className="nav-item dropdown">
                            <Link className="nav-link dropdown-toggle btnnavlink px-3 py-1" href="" id="navbarDropdown" role="button"
                                data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                                ProjectSeOps   </Link>

                            <div className="dropdown-menu" aria-labelledby="navbarDropdown">
                                <Link className="dropdown-item" href="">Action</Link>
                                <Link className="dropdown-item" href="">Another action</Link>
                                <div className="dropdown-divider"></div>
                                <Link className="dropdown-item" href="">Something else here</Link>
                            </div>
                        </li>
                        <li className="nav-item pl-2">
                            <Link className="nav-link btngrid px-2 py-1 text-white " href="">
                                <icon.FiMenu />
                            </Link>
                        </li>
                    </ul>
                    <form className="form-inline my-2 my-lg-0">
                        <ul className="navbar-nav">
                            <li className="pr-4">
                                <Link href="">
                                    <icon.FiMessageSquare />
                                </Link>
                            </li>
                            <li className="pr-4">
                                <Link href="">
                                    <icon.FiBell />
                                </Link>
                            </li>
                        </ul>
                        {/* <!-- Right side buttons Navigation bar --> */}
                        <div className="right-style">
                            <ul className="navbar-nav">
                                <li className="nav-item dropdown">
                                    <Link className="nav-link dropdown-toggle" href="" id="navbarDropdownMenuLink" role="button"
                                        data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">

                                        <icon.FaUserAstronaut />
                                        {/* <img src="photo-1556470234-36a5389f905a.jpg" width="40" height="40" className="rounded-circle" /> */}
                                                Reon Saji
                                        </Link>


                                    <div className="dropdown-menu" aria-labelledby="navbarDropdownMenuLink">
                                        <Link className="dropdown-item listitemscol" href="">Dashboard</Link>
                                        <Link className="dropdown-item listitemscol" href="">Edit Profile</Link>
                                        <Link className="dropdown-item listitemscol" href="">Log Out</Link>
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
