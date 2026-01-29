import React, { useState, useEffect, useCallback } from 'react';
import api from '../api';
import Toast from '../components/Toast';
import { usePermissions } from '../hooks/usePermissions';
import {
  FiMap, FiPlus, FiEdit2, FiTrash2, FiSearch, FiFilter,
  FiCheckCircle, FiXCircle, FiRefreshCw, FiGlobe, FiMapPin, FiFlag, FiTarget
} from 'react-icons/fi';
import './ZoneManagement.css';

const ZoneManagement = () => {
  console.log('ZoneManagement component rendered');
  const { canCreate, canEdit, canDelete } = usePermissions();
  
  const [zones, setZones] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [editingZone, setEditingZone] = useState(null);
  const [toast, setToast] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all'); // 'all', 'active', 'inactive'
  
  // Form state
  const [formData, setFormData] = useState({
    zone_name: '',
    country: '',
    state: '',
    city: '',
    priority: 0,
    status: true
  });
  const [formErrors, setFormErrors] = useState({});

  // Static data for dropdowns (can be replaced with API calls later)
  const countries = [
    { value: 'india', label: 'India' },
    { value: 'usa', label: 'United States' },
    { value: 'uk', label: 'United Kingdom' },
    { value: 'canada', label: 'Canada' },
    { value: 'australia', label: 'Australia' }
  ];

  const states = {
    india: [
      { value: 'andhra_pradesh', label: 'Andhra Pradesh' },
      { value: 'arunachal_pradesh', label: 'Arunachal Pradesh' },
      { value: 'assam', label: 'Assam' },
      { value: 'bihar', label: 'Bihar' },
      { value: 'chhattisgarh', label: 'Chhattisgarh' },
      { value: 'goa', label: 'Goa' },
      { value: 'gujarat', label: 'Gujarat' },
      { value: 'haryana', label: 'Haryana' },
      { value: 'himachal_pradesh', label: 'Himachal Pradesh' },
      { value: 'jharkhand', label: 'Jharkhand' },
      { value: 'karnataka', label: 'Karnataka' },
      { value: 'kerala', label: 'Kerala' },
      { value: 'madhya_pradesh', label: 'Madhya Pradesh' },
      { value: 'maharashtra', label: 'Maharashtra' },
      { value: 'manipur', label: 'Manipur' },
      { value: 'meghalaya', label: 'Meghalaya' },
      { value: 'mizoram', label: 'Mizoram' },
      { value: 'nagaland', label: 'Nagaland' },
      { value: 'odisha', label: 'Odisha' },
      { value: 'punjab', label: 'Punjab' },
      { value: 'rajasthan', label: 'Rajasthan' },
      { value: 'sikkim', label: 'Sikkim' },
      { value: 'tamil_nadu', label: 'Tamil Nadu' },
      { value: 'telangana', label: 'Telangana' },
      { value: 'tripura', label: 'Tripura' },
      { value: 'uttar_pradesh', label: 'Uttar Pradesh' },
      { value: 'uttarakhand', label: 'Uttarakhand' },
      { value: 'west_bengal', label: 'West Bengal' },
      { value: 'andaman_nicobar', label: 'Andaman and Nicobar Islands' },
      { value: 'chandigarh', label: 'Chandigarh' },
      { value: 'dadra_nagar_haveli', label: 'Dadra and Nagar Haveli and Daman and Diu' },
      { value: 'delhi', label: 'Delhi' },
      { value: 'jammu_kashmir', label: 'Jammu and Kashmir' },
      { value: 'ladakh', label: 'Ladakh' },
      { value: 'lakshadweep', label: 'Lakshadweep' },
      { value: 'puducherry', label: 'Puducherry' }
    ],
    usa: [
      { value: 'california', label: 'California' },
      { value: 'new_york', label: 'New York' },
      { value: 'texas', label: 'Texas' },
      { value: 'florida', label: 'Florida' }
    ],
    uk: [
      { value: 'england', label: 'England' },
      { value: 'scotland', label: 'Scotland' },
      { value: 'wales', label: 'Wales' }
    ],
    canada: [
      { value: 'ontario', label: 'Ontario' },
      { value: 'quebec', label: 'Quebec' },
      { value: 'british_columbia', label: 'British Columbia' }
    ],
    australia: [
      { value: 'new_south_wales', label: 'New South Wales' },
      { value: 'victoria', label: 'Victoria' },
      { value: 'queensland', label: 'Queensland' }
    ]
  };

  const cities = {
    andhra_pradesh: [
      { value: 'visakhapatnam', label: 'Visakhapatnam' },
      { value: 'vijayawada', label: 'Vijayawada' },
      { value: 'guntur', label: 'Guntur' },
      { value: 'nellore', label: 'Nellore' },
      { value: 'kurnool', label: 'Kurnool' },
      { value: 'rajahmundry', label: 'Rajahmundry' },
      { value: 'kakinada', label: 'Kakinada' },
      { value: 'tirupati', label: 'Tirupati' },
      { value: 'anantapur', label: 'Anantapur' },
      { value: 'kadapa', label: 'Kadapa' }
    ],
    arunachal_pradesh: [
      { value: 'itanagar', label: 'Itanagar' },
      { value: 'namsai', label: 'Namsai' },
      { value: 'pasighat', label: 'Pasighat' },
      { value: 'tezu', label: 'Tezu' },
      { value: 'bomdila', label: 'Bomdila' }
    ],
    assam: [
      { value: 'guwahati', label: 'Guwahati' },
      { value: 'silchar', label: 'Silchar' },
      { value: 'dibrugarh', label: 'Dibrugarh' },
      { value: 'jorhat', label: 'Jorhat' },
      { value: 'nagaon', label: 'Nagaon' },
      { value: 'tinsukia', label: 'Tinsukia' },
      { value: 'tezpur', label: 'Tezpur' },
      { value: 'sivasagar', label: 'Sivasagar' }
    ],
    bihar: [
      { value: 'patna', label: 'Patna' },
      { value: 'gaya', label: 'Gaya' },
      { value: 'bhagalpur', label: 'Bhagalpur' },
      { value: 'muzaffarpur', label: 'Muzaffarpur' },
      { value: 'purnia', label: 'Purnia' },
      { value: 'darbhanga', label: 'Darbhanga' },
      { value: 'bihar_sharif', label: 'Bihar Sharif' },
      { value: 'arrah', label: 'Arrah' },
      { value: 'begusarai', label: 'Begusarai' },
      { value: 'katihar', label: 'Katihar' }
    ],
    chhattisgarh: [
      { value: 'raipur', label: 'Raipur' },
      { value: 'bilaspur', label: 'Bilaspur' },
      { value: 'durg', label: 'Durg' },
      { value: 'rajnandgaon', label: 'Rajnandgaon' },
      { value: 'korba', label: 'Korba' },
      { value: 'raigarh', label: 'Raigarh' },
      { value: 'jagdalpur', label: 'Jagdalpur' },
      { value: 'ambikapur', label: 'Ambikapur' }
    ],
    goa: [
      { value: 'panaji', label: 'Panaji' },
      { value: 'margao', label: 'Margao' },
      { value: 'vasco_da_gama', label: 'Vasco da Gama' },
      { value: 'mapusa', label: 'Mapusa' },
      { value: 'ponda', label: 'Ponda' }
    ],
    gujarat: [
      { value: 'ahmedabad', label: 'Ahmedabad' },
      { value: 'surat', label: 'Surat' },
      { value: 'vadodara', label: 'Vadodara' },
      { value: 'rajkot', label: 'Rajkot' },
      { value: 'bhavnagar', label: 'Bhavnagar' },
      { value: 'jamnagar', label: 'Jamnagar' },
      { value: 'gandhinagar', label: 'Gandhinagar' },
      { value: 'anand', label: 'Anand' },
      { value: 'bharuch', label: 'Bharuch' },
      { value: 'mehsana', label: 'Mehsana' },
      { value: 'junagadh', label: 'Junagadh' },
      { value: 'gandhidham', label: 'Gandhidham' }
    ],
    haryana: [
      { value: 'gurgaon', label: 'Gurgaon' },
      { value: 'faridabad', label: 'Faridabad' },
      { value: 'panipat', label: 'Panipat' },
      { value: 'ambala', label: 'Ambala' },
      { value: 'yamunanagar', label: 'Yamunanagar' },
      { value: 'rohtak', label: 'Rohtak' },
      { value: 'hisar', label: 'Hisar' },
      { value: 'karnal', label: 'Karnal' },
      { value: 'sonipat', label: 'Sonipat' },
      { value: 'panchkula', label: 'Panchkula' }
    ],
    himachal_pradesh: [
      { value: 'shimla', label: 'Shimla' },
      { value: 'dharamshala', label: 'Dharamshala' },
      { value: 'solan', label: 'Solan' },
      { value: 'mandi', label: 'Mandi' },
      { value: 'kullu', label: 'Kullu' },
      { value: 'manali', label: 'Manali' },
      { value: 'palampur', label: 'Palampur' },
      { value: 'kangra', label: 'Kangra' }
    ],
    jharkhand: [
      { value: 'ranchi', label: 'Ranchi' },
      { value: 'jamshedpur', label: 'Jamshedpur' },
      { value: 'dhanbad', label: 'Dhanbad' },
      { value: 'bokaro', label: 'Bokaro' },
      { value: 'hazaribagh', label: 'Hazaribagh' },
      { value: 'giridih', label: 'Giridih' },
      { value: 'dumka', label: 'Dumka' },
      { value: 'deoghar', label: 'Deoghar' }
    ],
    karnataka: [
      { value: 'bangalore', label: 'Bangalore' },
      { value: 'mysore', label: 'Mysore' },
      { value: 'hubli', label: 'Hubli' },
      { value: 'mangalore', label: 'Mangalore' },
      { value: 'belgaum', label: 'Belgaum' },
      { value: 'gulbarga', label: 'Gulbarga' },
      { value: 'davangere', label: 'Davangere' },
      { value: 'bellary', label: 'Bellary' },
      { value: 'bijapur', label: 'Bijapur' },
      { value: 'shimoga', label: 'Shimoga' },
      { value: 'tumkur', label: 'Tumkur' },
      { value: 'raichur', label: 'Raichur' }
    ],
    kerala: [
      { value: 'kochi', label: 'Kochi' },
      { value: 'thiruvananthapuram', label: 'Thiruvananthapuram' },
      { value: 'kozhikode', label: 'Kozhikode' },
      { value: 'thrissur', label: 'Thrissur' },
      { value: 'kollam', label: 'Kollam' },
      { value: 'alappuzha', label: 'Alappuzha' },
      { value: 'kannur', label: 'Kannur' },
      { value: 'kottayam', label: 'Kottayam' },
      { value: 'palakkad', label: 'Palakkad' },
      { value: 'malappuram', label: 'Malappuram' }
    ],
    madhya_pradesh: [
      { value: 'bhopal', label: 'Bhopal' },
      { value: 'indore', label: 'Indore' },
      { value: 'gwalior', label: 'Gwalior' },
      { value: 'jabalpur', label: 'Jabalpur' },
      { value: 'raipur', label: 'Raipur' },
      { value: 'ujjain', label: 'Ujjain' },
      { value: 'sagar', label: 'Sagar' },
      { value: 'ratlam', label: 'Ratlam' },
      { value: 'burhanpur', label: 'Burhanpur' },
      { value: 'murwara', label: 'Murwara' }
    ],
    maharashtra: [
      { value: 'mumbai', label: 'Mumbai' },
      { value: 'pune', label: 'Pune' },
      { value: 'nagpur', label: 'Nagpur' },
      { value: 'thane', label: 'Thane' },
      { value: 'nashik', label: 'Nashik' },
      { value: 'aurangabad', label: 'Aurangabad' },
      { value: 'solapur', label: 'Solapur' },
      { value: 'amravati', label: 'Amravati' },
      { value: 'kolhapur', label: 'Kolhapur' },
      { value: 'sangli', label: 'Sangli' },
      { value: 'nanded', label: 'Nanded' },
      { value: 'jalgaon', label: 'Jalgaon' }
    ],
    manipur: [
      { value: 'imphal', label: 'Imphal' },
      { value: 'thoubal', label: 'Thoubal' },
      { value: 'bishnupur', label: 'Bishnupur' },
      { value: 'churachandpur', label: 'Churachandpur' }
    ],
    meghalaya: [
      { value: 'shillong', label: 'Shillong' },
      { value: 'tura', label: 'Tura' },
      { value: 'jowai', label: 'Jowai' },
      { value: 'nongpoh', label: 'Nongpoh' }
    ],
    mizoram: [
      { value: 'aizawl', label: 'Aizawl' },
      { value: 'lunglei', label: 'Lunglei' },
      { value: 'saiha', label: 'Saiha' },
      { value: 'champhai', label: 'Champhai' }
    ],
    nagaland: [
      { value: 'kohima', label: 'Kohima' },
      { value: 'dimapur', label: 'Dimapur' },
      { value: 'mokokchung', label: 'Mokokchung' },
      { value: 'tuensang', label: 'Tuensang' }
    ],
    odisha: [
      { value: 'bhubaneswar', label: 'Bhubaneswar' },
      { value: 'cuttack', label: 'Cuttack' },
      { value: 'rourkela', label: 'Rourkela' },
      { value: 'berhampur', label: 'Berhampur' },
      { value: 'sambalpur', label: 'Sambalpur' },
      { value: 'puri', label: 'Puri' },
      { value: 'balasore', label: 'Balasore' },
      { value: 'bhadrak', label: 'Bhadrak' }
    ],
    punjab: [
      { value: 'ludhiana', label: 'Ludhiana' },
      { value: 'amritsar', label: 'Amritsar' },
      { value: 'jalandhar', label: 'Jalandhar' },
      { value: 'patiala', label: 'Patiala' },
      { value: 'bathinda', label: 'Bathinda' },
      { value: 'mohali', label: 'Mohali' },
      { value: 'hoshiarpur', label: 'Hoshiarpur' },
      { value: 'batala', label: 'Batala' }
    ],
    rajasthan: [
      { value: 'jaipur', label: 'Jaipur' },
      { value: 'jodhpur', label: 'Jodhpur' },
      { value: 'kota', label: 'Kota' },
      { value: 'bikaner', label: 'Bikaner' },
      { value: 'ajmer', label: 'Ajmer' },
      { value: 'udaipur', label: 'Udaipur' },
      { value: 'bharatpur', label: 'Bharatpur' },
      { value: 'alwar', label: 'Alwar' },
      { value: 'sikar', label: 'Sikar' },
      { value: 'pali', label: 'Pali' }
    ],
    sikkim: [
      { value: 'gangtok', label: 'Gangtok' },
      { value: 'namchi', label: 'Namchi' },
      { value: 'mangan', label: 'Mangan' },
      { value: 'gyalshing', label: 'Gyalshing' }
    ],
    tamil_nadu: [
      { value: 'chennai', label: 'Chennai' },
      { value: 'coimbatore', label: 'Coimbatore' },
      { value: 'madurai', label: 'Madurai' },
      { value: 'tiruchirappalli', label: 'Tiruchirappalli' },
      { value: 'salem', label: 'Salem' },
      { value: 'tirunelveli', label: 'Tirunelveli' },
      { value: 'erode', label: 'Erode' },
      { value: 'vellore', label: 'Vellore' },
      { value: 'dindigul', label: 'Dindigul' },
      { value: 'thanjavur', label: 'Thanjavur' }
    ],
    telangana: [
      { value: 'hyderabad', label: 'Hyderabad' },
      { value: 'secunderabad', label: 'Secunderabad' },
      { value: 'warangal', label: 'Warangal' },
      { value: 'nizamabad', label: 'Nizamabad' },
      { value: 'karimnagar', label: 'Karimnagar' },
      { value: 'khammam', label: 'Khammam' },
      { value: 'mahabubnagar', label: 'Mahabubnagar' },
      { value: 'nalgonda', label: 'Nalgonda' },
      { value: 'adilabad', label: 'Adilabad' }
    ],
    tripura: [
      { value: 'agartala', label: 'Agartala' },
      { value: 'udaypur', label: 'Udaypur' },
      { value: 'kailasahar', label: 'Kailasahar' },
      { value: 'dharmanagar', label: 'Dharmanagar' }
    ],
    uttar_pradesh: [
      { value: 'lucknow', label: 'Lucknow' },
      { value: 'kanpur', label: 'Kanpur' },
      { value: 'agra', label: 'Agra' },
      { value: 'varanasi', label: 'Varanasi' },
      { value: 'meerut', label: 'Meerut' },
      { value: 'allahabad', label: 'Allahabad' },
      { value: 'ghaziabad', label: 'Ghaziabad' },
      { value: 'noida', label: 'Noida' },
      { value: 'bareilly', label: 'Bareilly' },
      { value: 'aligarh', label: 'Aligarh' },
      { value: 'moradabad', label: 'Moradabad' },
      { value: 'saharanpur', label: 'Saharanpur' }
    ],
    uttarakhand: [
      { value: 'dehradun', label: 'Dehradun' },
      { value: 'haridwar', label: 'Haridwar' },
      { value: 'roorkee', label: 'Roorkee' },
      { value: 'haldwani', label: 'Haldwani' },
      { value: 'rudrapur', label: 'Rudrapur' },
      { value: 'rishikesh', label: 'Rishikesh' },
      { value: 'nainital', label: 'Nainital' }
    ],
    west_bengal: [
      { value: 'kolkata', label: 'Kolkata' },
      { value: 'howrah', label: 'Howrah' },
      { value: 'durgapur', label: 'Durgapur' },
      { value: 'asansol', label: 'Asansol' },
      { value: 'siliguri', label: 'Siliguri' },
      { value: 'bardhaman', label: 'Bardhaman' },
      { value: 'malda', label: 'Malda' },
      { value: 'kharagpur', label: 'Kharagpur' },
      { value: 'cooch_behar', label: 'Cooch Behar' }
    ],
    andaman_nicobar: [
      { value: 'port_blair', label: 'Port Blair' },
      { value: 'rangat', label: 'Rangat' },
      { value: 'mayabunder', label: 'Mayabunder' }
    ],
    chandigarh: [
      { value: 'chandigarh', label: 'Chandigarh' }
    ],
    dadra_nagar_haveli: [
      { value: 'silvassa', label: 'Silvassa' },
      { value: 'daman', label: 'Daman' },
      { value: 'diu', label: 'Diu' }
    ],
    delhi: [
      { value: 'new_delhi', label: 'New Delhi' },
      { value: 'central_delhi', label: 'Central Delhi' },
      { value: 'north_delhi', label: 'North Delhi' },
      { value: 'south_delhi', label: 'South Delhi' },
      { value: 'east_delhi', label: 'East Delhi' },
      { value: 'west_delhi', label: 'West Delhi' },
      { value: 'north_east_delhi', label: 'North East Delhi' },
      { value: 'north_west_delhi', label: 'North West Delhi' },
      { value: 'south_west_delhi', label: 'South West Delhi' }
    ],
    jammu_kashmir: [
      { value: 'srinagar', label: 'Srinagar' },
      { value: 'jammu', label: 'Jammu' },
      { value: 'anantnag', label: 'Anantnag' },
      { value: 'baramulla', label: 'Baramulla' },
      { value: 'udhampur', label: 'Udhampur' }
    ],
    ladakh: [
      { value: 'leh', label: 'Leh' },
      { value: 'kargil', label: 'Kargil' }
    ],
    lakshadweep: [
      { value: 'kavaratti', label: 'Kavaratti' },
      { value: 'agatti', label: 'Agatti' },
      { value: 'minicoy', label: 'Minicoy' }
    ],
    puducherry: [
      { value: 'puducherry', label: 'Puducherry' },
      { value: 'karaikal', label: 'Karaikal' },
      { value: 'mahe', label: 'Mahe' },
      { value: 'yanam', label: 'Yanam' }
    ],
    california: [
      { value: 'los_angeles', label: 'Los Angeles' },
      { value: 'san_francisco', label: 'San Francisco' }
    ],
    new_york: [
      { value: 'new_york_city', label: 'New York City' },
      { value: 'buffalo', label: 'Buffalo' }
    ],
    texas: [
      { value: 'houston', label: 'Houston' },
      { value: 'dallas', label: 'Dallas' }
    ],
    florida: [
      { value: 'miami', label: 'Miami' },
      { value: 'tampa', label: 'Tampa' }
    ],
    england: [
      { value: 'london', label: 'London' },
      { value: 'manchester', label: 'Manchester' }
    ],
    scotland: [
      { value: 'edinburgh', label: 'Edinburgh' },
      { value: 'glasgow', label: 'Glasgow' }
    ],
    wales: [
      { value: 'cardiff', label: 'Cardiff' }
    ],
    ontario: [
      { value: 'toronto', label: 'Toronto' },
      { value: 'ottawa', label: 'Ottawa' }
    ],
    quebec: [
      { value: 'montreal', label: 'Montreal' },
      { value: 'quebec_city', label: 'Quebec City' }
    ],
    british_columbia: [
      { value: 'vancouver', label: 'Vancouver' },
      { value: 'victoria', label: 'Victoria' }
    ],
    new_south_wales: [
      { value: 'sydney', label: 'Sydney' },
      { value: 'newcastle', label: 'Newcastle' }
    ],
    victoria: [
      { value: 'melbourne', label: 'Melbourne' }
    ],
    queensland: [
      { value: 'brisbane', label: 'Brisbane' },
      { value: 'gold_coast', label: 'Gold Coast' }
    ]
  };

  // Get available states based on selected country
  const getAvailableStates = () => {
    if (!formData.country) return [];
    return states[formData.country] || [];
  };

  // Get available cities based on selected state
  const getAvailableCities = () => {
    if (!formData.state) return [];
    return cities[formData.state] || [];
  };

  // Fetch zones
  const fetchZones = useCallback(async () => {
    setLoading(true);
    try {
      const response = await api.get('zones/');
      
      if (response.data.message_type === 'success') {
        setZones(response.data.data || []);
      } else {
        setToast({
          message: 'Failed to fetch zones',
          type: 'error'
        });
      }
    } catch (error) {
      const errorMessage = error.response?.data?.error || 
                          error.response?.data?.message || 
                          'Failed to fetch zones';
      setToast({
        message: errorMessage,
        type: 'error'
      });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchZones();
  }, [fetchZones]);

  // Handle create/edit
  const handleSubmit = async (e) => {
    e.preventDefault();
    setFormErrors({});

    // Validation
    const errors = {};
    if (!formData.zone_name.trim()) {
      errors.zone_name = 'Zone name is required';
    }
    if (formData.priority < 0) {
      errors.priority = 'Priority must be 0 or greater';
    }

    if (Object.keys(errors).length > 0) {
      setFormErrors(errors);
      return;
    }

    setLoading(true);
    try {
      // Prepare payload according to API structure
      const payload = {
        zone_name: formData.zone_name.trim(),
        country: formData.country ? countries.find(c => c.value === formData.country)?.label || formData.country : null,
        state: formData.state ? (states[formData.country]?.find(s => s.value === formData.state)?.label || formData.state) : null,
        city: formData.city ? (cities[formData.state]?.find(c => c.value === formData.city)?.label || formData.city) : null,
        priority: formData.priority || 0,
        status: formData.status
      };

      let response;
      if (editingZone) {
        // Update zone - include zone_id for PUT
        payload.zone_id = editingZone.zone_id;
        response = await api.put(`zones/${editingZone.zone_id}/`, payload);
      } else {
        // Create zone
        response = await api.post('zones/', payload);
      }

      if (response.data.message_type === 'success') {
        setToast({
          message: editingZone ? 'Zone updated successfully!' : 'Zone created successfully!',
          type: 'success'
        });
        setShowModal(false);
        resetForm();
        fetchZones();
      } else {
        const errors = response.data.errors || {};
        setFormErrors(errors);
        setToast({
          message: 'Failed to save zone',
          type: 'error'
        });
      }
    } catch (error) {
      const errorData = error.response?.data;
      if (errorData?.errors) {
        setFormErrors(errorData.errors);
      }
      const errorMessage = errorData?.error || 
                          errorData?.message || 
                          'Failed to save zone';
      setToast({
        message: errorMessage,
        type: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  // Handle delete/disable
  const handleDelete = async (zoneId) => {
    if (!window.confirm('Are you sure you want to disable this zone?')) {
      return;
    }

    setLoading(true);
    try {
      const response = await api.delete(`zones/${zoneId}/`);
      
      if (response.data.message_type === 'success') {
        setToast({
          message: 'Zone disabled successfully!',
          type: 'success'
        });
        fetchZones();
      } else {
        setToast({
          message: 'Failed to disable zone',
          type: 'error'
        });
      }
    } catch (error) {
      const errorMessage = error.response?.data?.error || 
                          error.response?.data?.message || 
                          'Failed to disable zone';
      setToast({
        message: errorMessage,
        type: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  // Toggle zone status
  const handleToggleStatus = async (zone) => {
    setLoading(true);
    try {
      const updatedData = {
        zone_id: zone.zone_id,
        zone_name: zone.zone_name,
        country: zone.country || null,
        state: zone.state || null,
        city: zone.city || null,
        priority: zone.priority || 0,
        status: !(zone.status || zone.is_active)
      };
      
      const response = await api.put(`zones/${zone.zone_id}/`, updatedData);
      
      if (response.data.message_type === 'success') {
        setToast({
          message: `Zone ${(zone.status || zone.is_active) ? 'deactivated' : 'activated'} successfully!`,
          type: 'success'
        });
        fetchZones();
      }
    } catch (error) {
      const errorMessage = error.response?.data?.error || 
                          error.response?.data?.message || 
                          'Failed to update zone status';
      setToast({
        message: errorMessage,
        type: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  // Helper function to find country value from label
  const findCountryValue = (countryLabel) => {
    if (!countryLabel) return '';
    const country = countries.find(c => c.label === countryLabel);
    return country ? country.value : '';
  };

  // Helper function to find state value from label
  const findStateValue = (stateLabel, countryValue) => {
    if (!stateLabel || !countryValue) return '';
    const stateList = states[countryValue] || [];
    const state = stateList.find(s => s.label === stateLabel);
    return state ? state.value : '';
  };

  // Helper function to find city value from label
  const findCityValue = (cityLabel, stateValue) => {
    if (!cityLabel || !stateValue) return '';
    const cityList = cities[stateValue] || [];
    const city = cityList.find(c => c.label === cityLabel);
    return city ? city.value : '';
  };

  // Open modal for editing
  const handleEdit = (zone) => {
    setEditingZone(zone);
    const countryValue = findCountryValue(zone.country);
    const stateValue = findStateValue(zone.state, countryValue);
    const cityValue = findCityValue(zone.city, stateValue);
    
    setFormData({
      zone_name: zone.zone_name || '',
      country: countryValue,
      state: stateValue,
      city: cityValue,
      priority: zone.priority || 0,
      status: zone.status !== undefined ? zone.status : (zone.is_active !== undefined ? zone.is_active : true)
    });
    setShowModal(true);
  };

  // Open modal for creating
  const handleCreate = () => {
    setEditingZone(null);
    resetForm();
    setShowModal(true);
  };

  // Reset form
  const resetForm = () => {
    setFormData({
      zone_name: '',
      country: '',
      state: '',
      city: '',
      priority: 0,
      status: true
    });
    setFormErrors({});
  };

  // Handle country change - reset state and city
  const handleCountryChange = (country) => {
    setFormData({
      ...formData,
      country,
      state: '',
      city: ''
    });
  };

  // Handle state change - reset city
  const handleStateChange = (state) => {
    setFormData({
      ...formData,
      state,
      city: ''
    });
  };

  // Close modal
  const handleCloseModal = () => {
    setShowModal(false);
    setEditingZone(null);
    resetForm();
  };


  // Filter zones
  const filteredZones = zones.filter(zone => {
    const matchesSearch = (zone.zone_name || '').toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = filterStatus === 'all' || 
      (filterStatus === 'active' && (zone.status || zone.is_active)) ||
      (filterStatus === 'inactive' && !(zone.status || zone.is_active));
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="zone-management">
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}

      {/* Header */}
      <div className="zone-header">
        <div className="zone-title-section">
          <FiMap className="zone-title-icon" />
          <div>
            <h1 className="zone-title">Zone Management</h1>
            <p className="zone-subtitle">Manage geographic zones and surge pricing</p>
          </div>
        </div>
        {canCreate('/zones') && (
          <button className="btn btn-primary zone-create-btn" onClick={handleCreate}>
            <FiPlus className="me-2" />
            Create Zone
          </button>
        )}
      </div>

      {/* Filters and Search */}
      <div className="zone-filters">
        <div className="search-box">
          <FiSearch className="search-icon" />
          <input
            type="text"
            placeholder="Search zones..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>
        <div className="filter-group">
          <FiFilter className="filter-icon" />
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="filter-select"
          >
            <option value="all">All Zones</option>
            <option value="active">Active Only</option>
            <option value="inactive">Inactive Only</option>
          </select>
        </div>
        <button className="btn btn-secondary refresh-btn" onClick={fetchZones} disabled={loading}>
          <FiRefreshCw className={loading ? 'spinning' : ''} />
        </button>
      </div>

      {/* Zones List */}
      <div className="zones-container">
        {loading && zones.length === 0 ? (
          <div className="loading-state">
            <FiRefreshCw className="spinning" />
            <p>Loading zones...</p>
          </div>
        ) : filteredZones.length === 0 ? (
          <div className="empty-state">
            <FiMap className="empty-icon" />
            <p>No zones found</p>
            {canCreate('/zones') && (
              <button className="btn btn-primary" onClick={handleCreate}>
                Create Your First Zone
              </button>
            )}
          </div>
        ) : (
          <div className="zones-grid">
            {filteredZones.map((zone) => {
              const isActive = zone.status !== undefined ? zone.status : (zone.is_active !== undefined ? zone.is_active : true);
              return (
                <div key={zone.zone_id} className={`zone-card ${!isActive ? 'inactive' : ''}`}>
                  <div className="zone-card-header">
                    <div className="zone-card-title">
                      <h3>{zone.zone_name}</h3>
                      <span className={`status-badge ${isActive ? 'active' : 'inactive'}`}>
                        {isActive ? (
                          <>
                            <FiCheckCircle /> Active
                          </>
                        ) : (
                          <>
                            <FiXCircle /> Inactive
                          </>
                        )}
                      </span>
                    </div>
                    <div className="zone-card-actions">
                      {canEdit('/zones') && (
                        <button
                          className="btn-icon"
                          onClick={() => handleToggleStatus(zone)}
                          title={isActive ? 'Deactivate' : 'Activate'}
                        >
                          {isActive ? <FiXCircle /> : <FiCheckCircle />}
                        </button>
                      )}
                      {canEdit('/zones') && (
                        <button
                          className="btn-icon"
                          onClick={() => handleEdit(zone)}
                          title="Edit"
                        >
                          <FiEdit2 />
                        </button>
                      )}
                      {canDelete('/zones') && (
                        <button
                          className="btn-icon btn-icon-danger"
                          onClick={() => handleDelete(zone.zone_id)}
                          title="Disable"
                        >
                          <FiTrash2 />
                        </button>
                      )}
                    </div>
                  </div>

                  <div className="zone-card-body">
                    {zone.country && (
                      <div className="zone-info-item">
                        <span className="info-label">Country:</span>
                        <span className="info-value">
                          {zone.country}
                        </span>
                      </div>
                    )}
                    {zone.state && (
                      <div className="zone-info-item">
                        <span className="info-label">State:</span>
                        <span className="info-value">
                          {zone.state}
                        </span>
                      </div>
                    )}
                    {zone.city && (
                      <div className="zone-info-item">
                        <span className="info-label">City:</span>
                        <span className="info-value">
                          {zone.city}
                        </span>
                      </div>
                    )}
                    {zone.priority !== undefined && zone.priority !== null && (
                      <div className="zone-info-item">
                        <span className="info-label">Priority:</span>
                        <span className="info-value">
                          {zone.priority}
                        </span>
                      </div>
                    )}
                    <div className="zone-info-item">
                      <span className="info-label">Created:</span>
                      <span className="info-value">
                        {zone.created_at ? new Date(zone.created_at).toLocaleDateString() : 'N/A'}
                      </span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Create/Edit Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={handleCloseModal}>
          <div className="modal-content zone-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{editingZone ? 'Edit Zone' : 'Create New Zone'}</h2>
              <button className="modal-close" onClick={handleCloseModal}>×</button>
            </div>

            <form onSubmit={handleSubmit} className="zone-form">
              <div className="form-section">
                <div className="form-section-header">
                  <FiMap className="section-icon" />
                  <h3>Zone Information</h3>
                </div>
                <div className="form-section-content">
                  <div className="form-group">
                    <label htmlFor="zone_name" className="form-label">
                      <FiMapPin className="label-icon" />
                      Zone Name <span className="required">*</span>
                    </label>
                    <div className="input-wrapper">
                      <input
                        type="text"
                        id="zone_name"
                        value={formData.zone_name}
                        onChange={(e) => setFormData({ ...formData, zone_name: e.target.value })}
                        className={formErrors.zone_name ? 'error' : ''}
                        placeholder="e.g., Downtown Zone"
                      />
                    </div>
                    {formErrors.zone_name && (
                      <span className="error-message">{formErrors.zone_name}</span>
                    )}
                  </div>
                </div>
              </div>

              <div className="form-section">
                <div className="form-section-header">
                  <FiGlobe className="section-icon" />
                  <h3>Location Details</h3>
                </div>
                <div className="form-section-content">
                  <div className="form-group">
                    <label htmlFor="country" className="form-label">
                      <FiFlag className="label-icon" />
                      Country
                    </label>
                    <div className="select-wrapper">
                      <select
                        id="country"
                        value={formData.country}
                        onChange={(e) => handleCountryChange(e.target.value)}
                        className={formErrors.country ? 'error' : ''}
                      >
                        <option value="">Select Country (Optional)</option>
                        {countries.map(country => (
                          <option key={country.value} value={country.value}>
                            {country.label}
                          </option>
                        ))}
                      </select>
                    </div>
                    {formErrors.country && (
                      <span className="error-message">{formErrors.country}</span>
                    )}
                  </div>

                  <div className="form-group">
                    <label htmlFor="state" className="form-label">
                      <FiMapPin className="label-icon" />
                      State
                    </label>
                    <div className="select-wrapper">
                      <select
                        id="state"
                        value={formData.state}
                        onChange={(e) => handleStateChange(e.target.value)}
                        className={formErrors.state ? 'error' : ''}
                        disabled={!formData.country}
                      >
                        <option value="">{formData.country ? 'Select State (Optional)' : 'Select Country First'}</option>
                        {getAvailableStates().map(state => (
                          <option key={state.value} value={state.value}>
                            {state.label}
                          </option>
                        ))}
                      </select>
                    </div>
                    {formErrors.state && (
                      <span className="error-message">{formErrors.state}</span>
                    )}
                  </div>

                  <div className="form-group">
                    <label htmlFor="city" className="form-label">
                      <FiMapPin className="label-icon" />
                      City
                    </label>
                    <div className="select-wrapper">
                      <select
                        id="city"
                        value={formData.city}
                        onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                        className={formErrors.city ? 'error' : ''}
                        disabled={!formData.state}
                      >
                        <option value="">{formData.state ? 'Select City (Optional)' : 'Select State First'}</option>
                        {getAvailableCities().map(city => (
                          <option key={city.value} value={city.value}>
                            {city.label}
                          </option>
                        ))}
                      </select>
                    </div>
                    {formErrors.city && (
                      <span className="error-message">{formErrors.city}</span>
                    )}
                  </div>
                </div>
              </div>

              <div className="form-section">
                <div className="form-section-header">
                  <FiTarget className="section-icon" />
                  <h3>Zone Settings</h3>
                </div>
                <div className="form-section-content">
                  <div className="form-row">
                    <div className="form-group">
                      <label htmlFor="priority" className="form-label">
                        Priority Level
                      </label>
                      <div className="input-wrapper">
                        <input
                          type="number"
                          id="priority"
                          value={formData.priority}
                          onChange={(e) => setFormData({ ...formData, priority: parseInt(e.target.value) || 0 })}
                          className={formErrors.priority ? 'error' : ''}
                          min="0"
                          step="1"
                          placeholder="0"
                        />
                      </div>
                      {formErrors.priority && (
                        <span className="error-message">{formErrors.priority}</span>
                      )}
                      <small className="form-help">
                        Higher number = higher priority
                      </small>
                    </div>

                    <div className="form-group">
                      <label htmlFor="status" className="form-label">
                        Zone Status
                      </label>
                      <div className="toggle-container">
                        <div className="toggle-group">
                          <label className="toggle-switch">
                            <input
                              type="checkbox"
                              id="status"
                              checked={formData.status}
                              onChange={(e) => setFormData({ ...formData, status: e.target.checked })}
                            />
                            <span className="toggle-slider"></span>
                          </label>
                          <label htmlFor="status" className="toggle-label">
                            <span className={`status-text ${formData.status ? 'active' : 'inactive'}`}>
                              {formData.status ? 'Active' : 'Inactive'}
                            </span>
                          </label>
                        </div>
                        <small className="form-help">
                          {formData.status ? 'Zone is currently active' : 'Zone is currently inactive'}
                        </small>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="modal-actions">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={handleCloseModal}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <FiRefreshCw className="spinning me-2" />
                      Saving...
                    </>
                  ) : (
                    'Save Zone'
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default ZoneManagement;

