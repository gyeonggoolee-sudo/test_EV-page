# Database Schema Overview

## 1. ev_info
Tracks EV distribution quotas and real-time application status per region.
- **region_id**: (int) Unique identifier for the region.
- **notice_***: (int) Quota totals for categories (Total, Priority, Corp, Taxi, General).
- **appl_***: (int) Number of submitted applications.
- **release_***: (int) Number of vehicles released.
- **remain_***: (int) Remaining quota.
- **file_paths**: (jsonb) JSON object storing paths to related documents and check status.
- **bigo**: (text) Additional remarks or notes.

## 2. 공고문 (Public Notice)
Stores specific regulatory configurations and requirements for regional notices.
- **region_id**: (smallint) Primary Key.
- **notification_apply**: (jsonb) Configuration for application steps.
- **residence_requirements**: (int) Required days of residence (Default: 90).
- **co_name**: (jsonb) Mapping of company or organizational names.
- **notification_payment**: (jsonb) Details regarding payment requirements.
- **checked_status_list**: (jsonb) List of verified status flags.

## 3. ev_subsidies
Contains subsidy amounts for specific EV models in each region.
- **region_id**: (int) Foreign Key referencing region metadata.
- **model_name**: (text) Name/Code of the EV model.
- **national_subsidy**: (numeric) Central government subsidy.
- **local_subsidy**: (numeric) Regional government subsidy.
- **total_subsidy**: (numeric) Combined subsidy amount.

## 4. region_hp
Stores contact information for the departments in charge of each region.
- **region_id**: (int) Primary Key.
- **department**: (text) Name of the responsible department.
- **phone**: (text) Primary contact number.
- **phone_extra**: (text) Additional or alternative contact number.
