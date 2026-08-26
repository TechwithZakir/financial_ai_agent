import fs from "node:fs/promises";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const outputDir = new URL("../sample_data/", import.meta.url).pathname.replace(/^\/(.:)/, "$1");
await fs.mkdir(outputDir, { recursive: true });
const wb = Workbook.create();
const summary = wb.worksheets.add("Financial Statements");
const tx = wb.worksheets.add("Bank Transactions");
const checks = wb.worksheets.add("Checks");
summary.showGridLines = false; tx.showGridLines = false; checks.showGridLines = false;
summary.getRange("A1:D1").merge(); summary.getRange("A1").values = [["Northstar Trading Ltd. - Synthetic Financial Statements"]];
summary.getRange("A2:D2").merge(); summary.getRange("A2").values = [["Year ended 31 December 2025 | BDT | SYNTHETIC TEST DATA"]];
summary.getRange("A4:C4").values = [["Line Item", "2025", "2024"]];
summary.getRange("A5:C14").values = [
  ["Revenue",48500000,41200000],["Cost of sales",-32250000,-28400000],["Gross profit",16250000,12800000],
  ["Operating expenses",-9350000,-7400000],["Operating profit",6900000,5400000],["Finance costs",-1300000,-1050000],
  ["Tax expense",-1950000,-1640000],["Net income",3650000,2710000],["Total assets",32500000,28400000],["Total liabilities",16850000,14900000]
];
summary.getRange("D4").values = [["Change %"]]; summary.getRange("D5").formulas = [["=IF(C5=0,0,B5/C5-1)"]]; summary.getRange("D5:D14").fillDown();
summary.getRange("A1:D1").format = {fill:"#17365D",font:{bold:true,color:"#FFFFFF",size:16}};
summary.getRange("A2:D2").format = {fill:"#D9EAF7",font:{italic:true,color:"#17365D"}};
summary.getRange("A4:D4").format = {fill:"#2F75B5",font:{bold:true,color:"#FFFFFF"},borders:{preset:"outside",style:"thin",color:"#17365D"}};
summary.getRange("B5:C14").format.numberFormat = "#,##0;[Red](#,##0);-"; summary.getRange("D5:D14").format.numberFormat = "0.0%;[Red](0.0%);-";
summary.getRange("A1:D14").format.autofitColumns(); summary.getRange("A:A").format.columnWidth = 38; summary.getRange("B:C").format.columnWidth=17; summary.getRange("D:D").format.columnWidth=14; summary.freezePanes.freezeRows(4);

tx.getRange("A1:E1").values = [["Date","Description","Reference","Amount (BDT)","Balance (BDT)"]];
tx.getRange("A2:E9").values = [
  [new Date("2025-11-01"),"Opening balance","OPEN",0,1850000],[new Date("2025-11-03"),"Customer receipt - Orion Retail","CR-1042",1250000,3100000],
  [new Date("2025-11-05"),"Supplier payment - Delta Textiles","SP-883",-680000,2420000],[new Date("2025-11-10"),"Payroll","PAY-NOV",-420000,2000000],
  [new Date("2025-11-14"),"Customer receipt - Meridian Stores","CR-1057",910000,2910000],[new Date("2025-11-18"),"Loan repayment","LN-221",-275000,2635000],
  [new Date("2025-11-25"),"Utilities and rent","OPEX-77",-185000,2450000],[new Date("2025-11-30"),"Bank charges","BANK",-12500,2437500]
];
tx.getRange("A1:E1").format = {fill:"#17365D",font:{bold:true,color:"#FFFFFF"}}; tx.getRange("A2:A9").format.numberFormat="yyyy-mm-dd";
tx.getRange("D2:E9").format.numberFormat="#,##0.00;[Red](#,##0.00);-"; tx.getRange("A1:E9").format.autofitColumns(); tx.getRange("A:A").format.columnWidth=15; tx.getRange("B:B").format.columnWidth=38; tx.getRange("C:C").format.columnWidth=16; tx.getRange("D:E").format.columnWidth=19; tx.freezePanes.freezeRows(1);

checks.getRange("A1:E1").values=[["Check","Actual","Expected","Difference","Status"]];
checks.getRange("A2:E3").values=[["Assets equal liabilities plus equity",32500000,32500000,null,null],["Closing bank balance",2437500,2437500,null,null]];
checks.getRange("D2").formulas=[["=B2-C2"]]; checks.getRange("D2:D3").fillDown(); checks.getRange("E2").formulas=[["=IF(ABS(D2)<0.01,\"OK\",\"FAIL\")"]]; checks.getRange("E2:E3").fillDown();
checks.getRange("A1:E1").format={fill:"#17365D",font:{bold:true,color:"#FFFFFF"}}; checks.getRange("A1:E3").format.autofitColumns(); checks.getRange("A:A").format.columnWidth=42; checks.getRange("B:E").format.columnWidth=15;

const inspect = await wb.inspect({kind:"table",range:"Financial Statements!A1:D14",include:"values,formulas",tableMaxRows:20,tableMaxCols:8});
console.log(inspect.ndjson);
const errors = await wb.inspect({kind:"match",searchTerm:"#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",options:{useRegex:true,maxResults:50}}); console.log(errors.ndjson);
for (const sheetName of ["Financial Statements","Bank Transactions","Checks"]) {
  const preview = await wb.render({sheetName,autoCrop:"all",scale:1.5,format:"png"});
  await fs.writeFile(`${outputDir}/qa_${sheetName.replaceAll(" ","_")}.png`,new Uint8Array(await preview.arrayBuffer()));
}
const file = await SpreadsheetFile.exportXlsx(wb); await file.save(`${outputDir}/synthetic_financial_test_pack.xlsx`);
