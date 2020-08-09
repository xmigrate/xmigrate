import React, { Component } from 'react'
import "./SideNavbar.scss"
import { Link } from 'react-router-dom'
import * as icon from 'react-icons/all'
export default class SideNavbar extends Component {
    render() {
        return (
            <nav id="sidebarMenu" className=" SideNavbar col-md-3 col-lg-2 d-md-block bg-light sidebar collapse">
                <div className="sidebar-sticky pt-5 h-100 d-flex flex-column justify-content-between">
                    <ul className="nav flex-column">
                        <li className="nav-item p-3">
                            <Link className="nav-link active font-18" to="/discover">
                                <icon.FiHome /> Discovery
                                <span className="sr-only">(current)</span>
                            </Link>
                        </li>
                        <li className="nav-item p-3">
                            <Link className="nav-link font-18" to="/blue-print">
                                <icon.FiBox /> Blueprint
                            </Link>
                        </li>
                        <li className="nav-item p-3">
                            <Link className="nav-link font-18" to="/report">
                                <icon.BsMap /> Report
                            </Link>
                        </li>
                        <li className="nav-item p-3">
                            <Link className="nav-link font-18" to="/tutorials">
                                <icon.BsBook /> Tutorials
                            </Link>
                        </li>
                    </ul>
                    <div className="bottombar">
                        <p className="txtin"><Link className="bluelink" to="">invite your team</Link>
                         and <br />start collabrating!
                         </p>
                        <div className="bottomSettings">
                            <Link className="nav-link" to="/settings" >
                                <icon.FiSettings /> Settings   
                            </Link>
                        </div>
                    </div>
                </div>
            </nav>
        )
    }
}
