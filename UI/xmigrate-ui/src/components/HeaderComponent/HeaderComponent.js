import React, { Component } from 'react'
import { Link } from 'react-router-dom'
import * as icon from 'react-icons/all'
import "./HeaderComponent.scss"
import Auth from '../../services/Auth'
export default class HeaderComponent extends Component {
    constructor(props){
        super();
        console.log("loading the project",props.ProjectData);
        this.state={
            Projects : props.ProjectData,
        }
    }
 
    logout(e){
        Auth.logout(()=>{
        })   
    }
    
    render() {
        return (
            <div className="HeaderComponent">
                <nav className="navbar navbar-expand-lg navbar-light sticky-top bg-light flex-md-nowrap p-0 ">
                    <Link className="navbar-brand col-md-3 col-lg-2" to="">
                    <img
              src="Assets/images/logoSm.png"
              width="150"
              height="40"
              className="d-inline-block align-top"
              alt="xmigrate logo"
            />
                    </Link>
                    <button className="navbar-toggler position-absolute d-md-none collapsed" type="button" data-toggle="collapse"
                        data-target="#sidebarMenu" aria-controls="sidebarMenu" aria-expanded="false" aria-label="Toggle navigation">
                        <span className="navbar-toggler-icon"></span>
                    </button>
                    <ul className="navbar-nav mr-auto pl-4">
                        <li className="nav-item dropdown">
                            <div className="nav-link dropdown-toggle btnnavlink px-3 py-1" to="" id="navbarDropdown" role="button"
                                data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                                {this.props.CurrentPro.name}   </div>

                            <div className="dropdown-menu" aria-labelledby="navbarDropdown">

                                 {this.state.Projects.map((pro)=>(
                                     <div className="dropdown-item" key={pro.name} onClick={()=>this.props.onChangeProject(pro)}>{pro.name}</div>
                                ))} 
                             
                            </div>
                        </li>
                        <li className="nav-item pl-2">
                            {/* <Link className="nav-link btngrid px-2 py-1 text-white " to="/project"> */}
                            <Link className="nav-link px-2 py-1" to="/project">
                                <icon.BsPlusCircleFill className="btngrid" size={20}/>
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
                                                Admin
                                        </Link>


                                    <div className="dropdown-menu" aria-labelledby="navbarDropdownMenuLink">
                                        {/* <Link className="dropdown-item listitemscol" to="">Dashboard</Link> */}
                                        {/* <Link className="dropdown-item listitemscol" to="">Edit Profile</Link> */}
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
