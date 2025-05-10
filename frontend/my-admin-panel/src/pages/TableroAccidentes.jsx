import axios from "axios";
import "../styles/tablero_accidentes.css";
import React from "react";

const TableroAccidentes = () => {
    return (
        <div className="container">
            <iframe title="DASHBOARD PbI" width="1140" height="800"
                src="https://app.powerbi.com/reportEmbed?reportId=fbd18a43-df60-4b59-890c-85e2f46a7596&autoAuth=true&ctid=740be6bd-fd36-470e-94d9-0f0c777fadb9"
                frameborder="0" allowFullScreen="true">
            </iframe>
        </div>
    );
}
export default TableroAccidentes;