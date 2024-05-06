import React, { useState } from "react";
import { FaAnglesRight } from "react-icons/fa6";
import AgGridTable from "../Components/AgGridTable";
import { Button } from "antd";

function ShowLog({ data = [], setData }) {
  const [expandedLogs, setExpandedLogs] = useState([]);
  const toggleLog = (index) => {
    if (expandedLogs.includes(index)) {
      setExpandedLogs(expandedLogs.filter((i) => i !== index));
    } else {
      setExpandedLogs([...expandedLogs, index]);
    }
  };
const outputpanel= {
  resize: "both",
  overflow: "auto",
  minWidth: "400px", /* Adjust minimum width as needed */
  minHeight: "300px", /* Adjust minimum height as needed */
  // maxHeight: "calc(100vh - 250px)",
  backgroundColor:"#eaf0fd"
}

  return (
    <div className="overflow-hidden ">
      <div className="flex">
      <p className="font-secondary text-lg text-gray-800/85 font-semibold relative -top-2">
                Output
      </p>
      <div className="flex-grow"></div>
      <Button 
        className=" bg-blue-500 rounded text-white px-4"
        onClick={()=>setData([])}>
        Clear
      </Button>
      </div>
      <div
        className="h-full flex flex-col top-50 border-2"
        style={outputpanel}
      >
        {data.map((val, index) => (
          <div
            key={index}
            className={`flex items-start gap-3 border-b border-gray-300 ${
              expandedLogs.includes(index) ? "pb-4" : ""
            }`}
          >
            <div onClick={() => toggleLog(index)} className="cursor-pointer">
              <p>
                <FaAnglesRight size={15} />
              </p>
            </div>
            <div className="flex-1 color" style={{color: "green"}}>
              <p className="font-secondary text-lg text-gray-800/85 font-semibold relative -top-0">
                Output {index + 1}
              </p>
              {expandedLogs.includes(index) && (
                <div className="space-y-4">
                  {Object.keys(val).map((v, ind) => (
                    <React.Fragment key={ind}>
                      {val[v]["text"] && (
                        <p className="font-secondary text-lg text-gray-800/85 font-semibold relative -top-2">
                          {val[v]["text"]}
                        </p>
                      )}
                      {val[v]["table"] && val[v]["table"].length > 0 && (
                        <AgGridTable rowData={val[v]["table"]} />
                      )}
                      {val[v]["graph"] && (
                        <img
                          src={`data:image/png;base64,${val[v]["graph"]}`}
                          alt=""
                        />
                      )}
                    </React.Fragment>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default ShowLog;
