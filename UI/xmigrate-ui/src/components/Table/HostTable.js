import { useState } from 'react';
import {Table} from "react-bootstrap";
import {BsCaretDownFill,BsCaretRightFill} from "react-icons/bs";
import { IconContext } from "react-icons";
import "./NetworkTable.scss";

export default function HostTable(props) {

    const [expanderDisk,toggleExpanderDisk] = useState(false);

    return (
        <tbody className="HostTable">
        <tr className="HostRow"  key={props.index} onClick={()=>{toggleExpanderDisk(!expanderDisk)}}>
        <td >{ expanderDisk ? <IconContext.Provider value={{ color: "#1DA1F2" }}>
  <div>
  <BsCaretDownFill  /> 
  </div>
</IconContext.Provider> :  <BsCaretRightFill /> } 
           </td>
        <td>{props.data.id}</td>
        <td>{props.data.hostname}</td>
        <td>{props.data.ip}</td>
        <td>{props.data.subnet}</td>
        <td>{props.data.network}</td>
        <td>{props.data.cpu}</td>
        <td>{props.data.core}</td>
        <td>{props.data.ram}</td>
      </tr>
      <tr>
          <td colSpan={9}>
          <div>
          {expanderDisk &&(
        <Table className="bordered hover">
        <thead>
            <tr>
                <th> mnt_path</th>
                <th>disk_size</th>
                <th>uuid</th>
                <th>dev</th>
                <th>filesystem</th>
            </tr>
            </thead>
       
            <tbody>
          
            {props.data.disk.map((data, index) => (
            <tr key={index}>
                <td>{data.mnt_path}</td>
                <td>{data.disk_size}</td>
                <td>{data.uuid}</td>
                <td>{data.dev}</td>
                <td>{data.filesystem}</td>
            </tr>
        
             ))}
               
            </tbody>
         
       
        </Table>
            )}
        </div>
        </td>
        </tr>
        </tbody>
   
    )
}