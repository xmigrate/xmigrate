import React, { Component } from "react";
import HeaderComponent from "../../components/HeaderComponent/HeaderComponent";
import SideNavbar from "../../components/SideNavbar/SideNavbar";
import BluePrint from "../BluePrint/BluePrint";
import Discover from "../Discover/Discover";
import Loader from "../../components/Loader/Loader";
import { ProtectedRoute } from "../../services/Protected.route";
import GetService,{GetServiceWithData} from "../../services/GetService";
import { GETPROJECTS,BLUEPRINT_URL } from "../../services/Services";
import Settings from "../Settings/Settings";
import { useHistory } from "react-router-dom";
export default class Home extends Component {
  constructor(props) {
    super();
    this.state = {
      Projects: [],
      Loading: true,
      CurrentPro: "Default",
      BlueprintDisabled:true
    };
    this.changeProject = this.changeProject.bind(this);
  }

  async componentDidMount() {
    this.setState({
      Loading:true
    });
    let noProject  = true;
    let ProjectDetails;
    // Func:Getting the projects of user by calling Funtion with authentication id user id identified
    await GetService(GETPROJECTS).then((res) => {
      if (res.data === "[]") {
        this.props.history.push("/project");
      } else {
        noProject = false;
        ProjectDetails = JSON.parse(res.data);
      }

    });
    if(noProject==false){

   
        var CurrentProject ;
        //Setting Which Needs to be the Current Project on loading
        if (typeof this.props.state !== "undefined") {
          CurrentProject =  this.props.state.detail;
        }
        else{
          CurrentProject = ProjectDetails[0];
        }
        let dataGet ={
          project: CurrentProject.name
        }
        console.log("The Current Project",CurrentProject.name);
        let BlueprintDisabled = true;
        let BlueprintData;
       await GetServiceWithData(BLUEPRINT_URL, dataGet).then(
          (res) => {
            console.log(res.data);
            if(JSON.parse(res.data).length === 0){
              BlueprintDisabled = true;
            }
            else{
              BlueprintDisabled = false;
              BlueprintData = res.data;
            }
          }
        );
        this.setState({
          Projects: ProjectDetails,
          Loading: false,
          CurrentPro: CurrentProject,
          BlueprintDisabled : BlueprintDisabled,
          BlueprintData:BlueprintData
        });
      }
   
  }

  // Func:Changing the project state when clicking the sidebar by call back Funtion
  async changeProject(project) {
    console.log("Changine Project",project);
    var dataGet ={
      project: project.name
    }
    let BlueprintDisabled ;
    this.setState({
      Loading:true
    });
    await GetServiceWithData(BLUEPRINT_URL, dataGet).then(
      (res) => {
        if(JSON.parse(res.data).length === 0){
          BlueprintDisabled = true;
        }
        else{
          BlueprintDisabled = false;
        }
      }
    );
    this.setState({
      CurrentPro: project,
      BlueprintDisabled : BlueprintDisabled,
      Loading:false
    });
    if(BlueprintDisabled && this.props.location.pathname ==='/home/blue-print'){
      this.props.history.push('/home/discover');
    }
  }

  render() {
    if (this.state.Loading) {
      return <Loader />;
    } else {
      return (
        <div className="Home h-100 d-flex flex-column">
          <HeaderComponent
            ProjectData={this.state.Projects}
            CurrentPro={this.state.CurrentPro}
            onChangeProject={this.changeProject}
          />
          <div className="container-fluid media-body ">
            <div className="row h-100">
              <SideNavbar BlueprintDis={this.state.BlueprintDisabled}  />
              <ProtectedRoute
                exact
                strict
                path="/home/blue-print"
                component={() => (
                  <BluePrint CurrentPro={this.state.CurrentPro} BluePrintData={this.state.BlueprintData} />
                )}
              />
              <ProtectedRoute
                exact
                strict
                path="/home/discover"
                component={() => (
                  <Discover
                    ProjectData={this.state.Projects}
                    CurrentPro={this.state.CurrentPro}
                  />
                )}
              />
              <ProtectedRoute
                exact
                strict
                path="/home/settings"
                component={() => (
                  <Settings CurrentPro={this.state.CurrentPro} />
                )}
              />
            </div>
          </div>
        </div>
      );
    }
  }
}
